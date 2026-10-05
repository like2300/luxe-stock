/* Bouton « Scanner » du formulaire produit : remplit le champ code-barres
   avec la caméra (BarcodeDetector natif, sinon html5-qrcode en secours). */
(function () {
    "use strict";

    var btn = document.getElementById("barcode-scan-btn");
    if (!btn) { return; }

    var input = document.getElementById(btn.dataset.scanTarget);
    var box = document.getElementById("barcode-camera");
    var video = document.getElementById("barcode-video");
    var region = document.getElementById("barcode-camera-region");
    var message = document.getElementById("barcode-camera-message");
    var scanner = null, stream = null, loop = null;

    function say(text, toneName) {
        message.textContent = text;
        message.className = "hidden mt-2 text-sm rounded-lg px-3 py-2 " + (
            toneName === "ko" ? "bg-rose-50 text-rose-700" : "bg-orange-50 text-orange-700"
        );
        message.classList.remove("hidden");
    }

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

    function fill(code) {
        input.value = String(code).trim();
        input.dispatchEvent(new Event("input", { bubbles: true }));
        stop();
    }

    function fail(error) {
        var name = String((error && (error.name || error.message)) || "");
        if (name.indexOf("NotAllowed") !== -1 || name.indexOf("Permission") !== -1) {
            say("Caméra refusée : autorisez l'accès dans votre navigateur.", "ko");
        } else if (name.indexOf("NotFound") !== -1 || name.indexOf("NotReadable") !== -1) {
            say("Aucune caméra disponible. Saisissez le code à la main.", "ko");
        } else {
            say("Caméra indisponible (" + (name || "erreur inconnue") + ").", "ko");
        }
        stop();
    }

    function startNative() {
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
            .then(function (media) {
                stream = media;
                video.srcObject = media;
                video.setAttribute("playsinline", "");
                video.play();
                var detector = new window.BarcodeDetector({
                    formats: ["ean_13", "ean_8", "upc_a", "upc_e", "code_128", "code_39", "itf", "qr_code", "codabar"]
                });
                var tick = function () {
                    detector.detect(video)
                        .then(function (codes) { if (codes && codes.length) { fill(codes[0].rawValue); } })
                        .catch(function () { })
                        .then(function () { if (stream) { loop = requestAnimationFrame(tick); } });
                };
                loop = requestAnimationFrame(tick);
            })
            .catch(fail);
    }

    function startFallback() {
        loadHtml5QrCode()
            .then(function () {
                scanner = new window.Html5Qrcode("barcode-camera-region");
                return scanner.start(
                    { facingMode: "environment" },
                    { fps: 10, qrbox: { width: 280, height: 120 } },
                    fill,
                    function () { }
                );
            })
            .catch(fail);
    }

    function start() {
        if (!(window.isSecureContext || location.hostname === "localhost" || location.hostname === "127.0.0.1")) {
            say("La caméra exige une page sécurisée : ouvrez le site en HTTPS.", "ko");
            return;
        }
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            say("Ce navigateur ne donne pas accès à la caméra.", "ko");
            return;
        }
        box.classList.remove("hidden");
        message.classList.add("hidden");
        if (window.BarcodeDetector) { startNative(); } else { startFallback(); }
    }

    function stop() {
        if (loop) { cancelAnimationFrame(loop); loop = null; }
        if (scanner) {
            scanner.stop().catch(function () { });
            scanner.clear();
            scanner = null;
        }
        if (stream) {
            stream.getTracks().forEach(function (track) { track.stop(); });
            stream = null;
        }
        video.srcObject = null;
        box.classList.add("hidden");
    }

    btn.addEventListener("click", start);
    window.addEventListener("pagehide", stop);
})();