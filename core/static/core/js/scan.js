/* Scanner de codes-barres : saisie clavier (scanners USB/Bluetooth) ou caméra.
   Le lot est envoyé en un appel à /api/scan/mouvement/ (CSRF fourni par Django). */
(function () {
    "use strict";

    var DUP_MS = 800;          // Deux lectures du même code dans ce délai sont ignorées.
    var MODE_OUT = "OUT";
    var MODE_IN = "IN";
    var MODE_CARD = "CARD";
    var LEVEL_CLASS = { rupture: "bg-rose-100 text-rose-700", bas: "bg-orange-100 text-orange-700", ok: "bg-emerald-100 text-emerald-700" };

    var root = document.getElementById("scan-app");
    if (!root) { return; }

    var cfg = {
        lookupUrl: root.dataset.lookupUrl,
        postUrl: root.dataset.postUrl,
        createUrl: root.dataset.createUrl,
        editUrl: root.dataset.editUrl,
        canManage: root.dataset.canManage === "1",
        canAdd: root.dataset.canAdd === "1",
        canEdit: root.dataset.canEdit === "1"
    };

    var input = document.getElementById("scan-input");
    var lines = document.getElementById("scan-lines");
    var statusBox = document.getElementById("scan-status");
    var emptyBox = document.getElementById("scan-empty");
    var validateBtn = document.getElementById("scan-validate");
    var resetBtn = document.getElementById("scan-reset");
    var clearBtn = document.getElementById("scan-clear");
    var noteInput = document.getElementById("scan-note");
    var cameraBox = document.getElementById("scan-camera");
    var cameraBtn = document.getElementById("scan-camera-btn");
    var cameraStopBtn = document.getElementById("scan-camera-stop");
    var cameraVideo = document.getElementById("scan-camera-video");

    var mode = root.dataset.mode || MODE_OUT;
    var cart = [];             // [{id, name, sku, stock, level, quantity}]
    var lastCode = "", lastAt = 0;

    /* ---------- Sons (Web Audio API, aucun fichier) ---------- */
    function beepOk() {
        tone(880, 0, 0.09);
        tone(1320, 0.1, 0.12);
    }
    function beepKo() {
        tone(200, 0, 0.16);
        tone(140, 0.18, 0.28);
    }
    function tone(freq, delay, duration) {
        var Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) { return; }
        var ctx = beepOk.ctx || (beepOk.ctx = new Ctx());
        if (ctx.state === "suspended") { ctx.resume(); }
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        var start = ctx.currentTime + delay;
        osc.type = "sine";
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.0001, start);
        gain.gain.exponentialRampToValueAtTime(0.25, start + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, start + duration);
        osc.connect(gain).connect(ctx.destination);
        osc.start(start);
        osc.stop(start + duration + 0.02);
    }

    function escapeHtml(value) {
        return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
        });
    }

    function say(text, toneName) {
        statusBox.textContent = text;
        statusBox.className = "px-4 py-2.5 rounded-xl text-sm font-medium " + (
            toneName === "ko" ? "bg-rose-50 text-rose-700 border border-rose-100"
                : toneName === "warn" ? "bg-orange-50 text-orange-700 border border-orange-100"
                    : "bg-emerald-50 text-emerald-700 border border-emerald-100"
        );
        statusBox.classList.remove("hidden");
        if (toneName === "ko") { beepKo(); } else { beepOk(); }
    }

    /* ---------- Modes ---------- */
    function setMode(next) {
        // Sans droit de gestion du stock, seuls la fiche produit est possible.
        if (!cfg.canManage && next !== MODE_CARD) { next = MODE_CARD; }
        mode = next;
        var moves = cfg.canManage && next !== MODE_CARD;
        root.dataset.mode = next;
        document.getElementById("scan-create-box").classList.toggle("hidden", true);

        Array.prototype.forEach.call(document.querySelectorAll("[data-mode-btn]"), function (btn) {
            var on = btn.getAttribute("data-mode-btn") === next;
            btn.setAttribute("aria-pressed", on ? "true" : "false");
            btn.className = "flex-1 px-3 py-3 rounded-xl text-sm font-semibold border-2 transition-all duration-200 " + (on
                ? "border-transparent bg-primary text-white shadow-lg shadow-primary/30"
                : "border-slate-200 bg-white text-slate-500 hover:border-primary/40 hover:text-primary");
        });

        Array.prototype.forEach.call(document.querySelectorAll("[data-mode-only]"), function (el) {
            var allowed = el.getAttribute("data-mode-only").split(" ").indexOf(next) !== -1;
            el.classList.toggle("hidden", !allowed);
        });

        var title = document.getElementById("scan-mode-title");
        if (title) {
            title.textContent = next === MODE_IN ? "Entrée de stock (réception)"
                : next === MODE_CARD ? "Fiche produit"
                    : "Sortie de stock (vente)";
        }
        if (validateBtn) { validateBtn.classList.toggle("hidden", !moves); }
        render();
    }

    /* ---------- Liste ---------- */
    function findLine(id) {
        for (var i = 0; i < cart.length; i++) {
            if (cart[i].id === id) { return cart[i]; }
        }
        return null;
    }

    function addLine(product) {
        var existing = findLine(product.id);
        if (existing) {
            // Rescanner le meme produit augmente sa quantite de 1.
            existing.quantity += 1;
        } else {
            cart.push({
                id: product.id, name: product.name, sku: product.sku,
                stock: Number(product.stock) || 0, level: product.level, quantity: 1
            });
        }
        render();
    }

    function render() {
        if (!lines) { return; }
        if (!cart.length) {
            lines.innerHTML = "";
            emptyBox.classList.remove("hidden");
            if (validateBtn) { validateBtn.disabled = true; }
            return;
        }
        emptyBox.classList.add("hidden");
        if (validateBtn) { validateBtn.disabled = false; }

        lines.innerHTML = cart.map(function (item, index) {
            var badge = LEVEL_CLASS[item.level] || LEVEL_CLASS.ok;
            return '<li class="flex flex-wrap items-center gap-3 px-4 py-3 border-b border-slate-50 last:border-0">'
                + '<div class="min-w-0 flex-1">'
                + '<p class="text-sm font-semibold text-slate-700 truncate">' + escapeHtml(item.name) + "</p>"
                + '<p class="text-xs text-slate-400 truncate">' + escapeHtml(item.sku || "Sans référence") + "</p>"
                + "</div>"
                + '<span class="px-2.5 py-0.5 rounded-full text-xs font-medium ' + badge + '">'
                + item.stock + " en stock</span>"
                + '<label class="sr-only" for="scan-qty-' + index + '">Quantité pour ' + escapeHtml(item.name) + "</label>"
                + '<input id="scan-qty-' + index + '" type="number" min="1" step="1" value="' + item.quantity
                + '" data-role="qty" data-index="' + index
                + '" class="w-20 px-3 py-2 rounded-lg border border-slate-200 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary">'
                + '<button type="button" data-role="remove" data-index="' + index
                + '" class="p-2 rounded-full text-slate-400 hover:bg-rose-50 hover:text-rose-500 transition-colors" title="Retirer">'
                + '<iconify-icon icon="solar:trash-bin-minimalistic-linear" width="18"></iconify-icon>'
                + "</button></li>";
        }).join("");
    }

    /* ---------- Recherche d'un code ---------- */
    function lookup(rawCode) {
        var code = String(rawCode || "").replace(/\s+/g, "");
        if (!code) { return; }

        var now = Date.now();
        if (code === lastCode && now - lastAt < DUP_MS) { focusInput(); return; }
        lastCode = code;
        lastAt = now;

        fetch(cfg.lookupUrl + "?code=" + encodeURIComponent(code), {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data && data.found) {
                    onFound(data);
                } else {
                    onNotFound(code);
                }
            })
            .catch(function () {
                say("Recherche impossible : le serveur ne répond pas.", "ko");
            })
            .then(focusInput);
    }

    function onFound(product) {
        if (mode === MODE_CARD) {
            showCard(product);
            return;
        }
        addLine(product);
        say(product.name + " ajouté.", "ok");
    }

    function showCard(product) {
        // Mode fiche produit : on affiche la fiche sur place (pas de navigation),
        // l'utilisateur peut enchaîner les scans.
        var box = document.getElementById("scan-card");
        var badge = LEVEL_CLASS[product.level] || LEVEL_CLASS.ok;
        box.innerHTML =
            '<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Fiche produit</p>'
            + '<h2 class="text-xl font-bold text-dark">' + escapeHtml(product.name) + "</h2>"
            + '<p class="text-sm text-slate-400">' + escapeHtml(product.sku || "Sans référence") + "</p>"
            + '<div class="flex flex-wrap items-center gap-3 mt-4">'
            + '<span class="px-3 py-1 rounded-full text-xs font-medium ' + badge + '">'
            + product.stock + " en stock</span>"
            + '<span class="px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600">'
            + escapeHtml(product.category || "Sans catégorie") + "</span>"
            + "</div>";
        box.classList.remove("hidden");
        if (cfg.canEdit) {
            var link = document.getElementById("scan-card-edit");
            link.href = cfg.editUrl.replace("0", String(product.id));
            link.classList.remove("hidden");
        }
        say(product.name + " — " + product.stock + " en stock.", "ok");
    }

    function onNotFound(code) {
        say("Produit introuvable : " + code, "ko");
        var box = document.getElementById("scan-create-box");
        var link = document.getElementById("scan-create-link");
        if (box && link) {
            box.classList.remove("hidden");
            link.href = cfg.createUrl + "?barcode=" + encodeURIComponent(code);
        }
    }

    function focusInput() {
        if (input && document.activeElement !== input && document.activeElement.tagName !== "INPUT") {
            input.focus();
        }
    }

    /* ---------- Caméra ---------- */
    function isSecureForCamera() {
        return window.isSecureContext || location.hostname === "localhost"
            || location.hostname === "127.0.0.1";
    }

    var scanner = null, stream = null, detectLoop = null;

    function loadHtml5QrCode() {
        if (window.Html5Qrcode) { return Promise.resolve(); }
        return new Promise(function (resolve, reject) {
            var s = document.createElement("script");
            s.src = "https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js";
            s.onload = resolve;
            s.onerror = function () { reject(new Error("Chargement impossible")); };
            document.head.appendChild(s);
        });
    }

    function startBarcodeDetector() {
        // BarcodeDetector natif (Chrome/Edge/Android) : aucun script à charger.
        var Detector = window.BarcodeDetector;
        if (!Detector) { return startHtml5QrCode(); }

        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
            .then(function (media) {
                stream = media;
                cameraVideo.srcObject = media;
                cameraVideo.setAttribute("playsinline", "");
                cameraVideo.play();
                var detector = new Detector({
                    formats: ["ean_13", "ean_8", "upc_a", "upc_e", "code_128", "code_39", "itf", "qr_code", "codabar"]
                });
                var tick = function () {
                    detector.detect(cameraVideo)
                        .then(function (codes) {
                            if (codes && codes.length) { lookup(codes[0].rawValue); }
                        })
                        .catch(function () { })
                        .then(function () {
                            detectLoop = requestAnimationFrame(tick);
                        });
                };
                detectLoop = requestAnimationFrame(tick);
                say("Caméra active : présentez le code-barres.", "ok");
            })
            .catch(function (error) { cameraError(error); });
    }

    function startHtml5QrCode() {
        loadHtml5QrCode()
            .then(function () {
                scanner = new window.Html5Qrcode("scan-camera-region");
                return scanner.start(
                    { facingMode: "environment" },
                    { fps: 10, qrbox: { width: 280, height: 160 } },
                    function (text) { lookup(text); },
                    function () { }
                );
            })
            .then(function () { say("Caméra active : présentez le code-barres.", "ok"); })
            .catch(function (error) { cameraError(error); });
    }

    function cameraError(error) {
        var name = (error && (error.name || error.message)) || "";
        if (String(name).indexOf("NotAllowed") !== -1 || String(name).indexOf("Permission") !== -1) {
            say("Caméra refusée : autorisez l'accès à la caméra dans votre navigateur.", "ko");
        } else if (String(name).indexOf("NotFound") !== -1 || String(name).indexOf("NotReadable") !== -1) {
            say("Aucune caméra disponible sur cet appareil.", "ko");
        } else {
            say("Caméra indisponible (" + (name || "erreur inconnue") + ").", "ko");
        }
        stopCamera();
    }

    function startCamera() {
        if (!isSecureForCamera()) {
            say("La caméra exige une page sécurisée : ouvrez le site en HTTPS (ou sur localhost).", "warn");
            return;
        }
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            say("Ce navigateur ne donne pas accès à la caméra. Utilisez la saisie clavier.", "warn");
            return;
        }
        cameraBox.classList.remove("hidden");
        cameraBtn.classList.add("hidden");
        cameraStopBtn.classList.remove("hidden");
        startBarcodeDetector();
    }

    function stopCamera() {
        if (detectLoop) { cancelAnimationFrame(detectLoop); detectLoop = null; }
        if (scanner) {
            scanner.stop().catch(function () { });
            scanner.clear();
            scanner = null;
        }
        if (stream) {
            stream.getTracks().forEach(function (track) { track.stop(); });
            stream = null;
        }
        cameraVideo.srcObject = null;
        cameraBox.classList.add("hidden");
        cameraBtn.classList.remove("hidden");
        cameraStopBtn.classList.add("hidden");
    }

    /* ---------- Envoi du lot ---------- */
    function submit() {
        if (!cart.length) { return; }
        if (mode === MODE_CARD) { return; }

        var items = cart.map(function (item) {
            return { product_id: item.id, quantity: item.quantity };
        });
        validateBtn.disabled = true;
        say("Enregistrement en cours...", "ok");

        fetch(cfg.postUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({
                items: items,
                kind: mode,
                note: noteInput ? noteInput.value : ""
            })
        })
            .then(function (r) {
                return r.json().then(function (data) { return { ok: r.ok, data: data }; });
            })
            .then(function (res) {
                if (!res.ok || !res.data.ok) {
                    say((res.data.errors || ["Enregistrement refusé."]).join(" "), "ko");
                    validateBtn.disabled = false;
                    return;
                }
                say(res.data.count + " ligne(s) enregistrée(s).", "ok");
                cart = [];
                render();
            })
            .catch(function () {
                say("Enregistrement impossible : le serveur ne répond pas.", "ko");
                validateBtn.disabled = false;
            });
    }

    function getCookie(name) {
        var match = document.cookie.match(new RegExp("(?:^|;\\s*)" + name + "=([^;]*)"));
        return match ? decodeURIComponent(match[1]) : "";
    }

    /* ---------- Écouteurs ---------- */
    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            lookup(input.value);
            input.value = "";
        }
    });

    // Un scanner USB « tape » le code puis valide ; la page doit rester prête.
    document.addEventListener("click", function () { focusInput(); });

    lines.addEventListener("change", function (event) {
        var index = event.target.getAttribute("data-role") === "qty" ? event.target.getAttribute("data-index") : null;
        if (index === null) { return; }
        var value = parseInt(event.target.value, 10);
        if (isNaN(value) || value < 1) {
            event.target.value = cart[index].quantity;
            say("La quantité doit être au moins 1.", "ko");
            return;
        }
        cart[index].quantity = value;
        focusInput();
    });

    lines.addEventListener("click", function (event) {
        var btn = event.target.closest('[data-role="remove"]');
        if (!btn) { return; }
        cart.splice(Number(btn.getAttribute("data-index")), 1);
        render();
        focusInput();
    });

    Array.prototype.forEach.call(document.querySelectorAll("[data-mode-btn]"), function (btn) {
        btn.addEventListener("click", function () {
            setMode(btn.getAttribute("data-mode-btn"));
        });
    });

    cameraBtn.addEventListener("click", startCamera);
    cameraStopBtn.addEventListener("click", stopCamera);
    validateBtn.addEventListener("click", submit);
    clearBtn.addEventListener("click", function () {
        cart = [];
        render();
        say("Liste vidée.", "ok");
        focusInput();
    });
    resetBtn.addEventListener("click", function () {
        cart = [];
        render();
        if (noteInput) { noteInput.value = ""; }
        focusInput();
    });

    setMode(mode);
    input.focus();
})();