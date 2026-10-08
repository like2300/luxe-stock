/* Alertes flottantes façon iOS : cartes empilées en bas à droite, fermées au
   clic ou seules au bout de quelques secondes.

   Toutes les alertes de l'application passent par cette couche unique : les
   messages Django et les notifications de la boutique arrivent dans #toast-queue
   (rendu par base.html), et les scripts appellent window.toast(...) ou
   window.StkToast.success/error/warning/info(...). */
(function () {
    "use strict";

    var LAYER_ID = "toast-layer";
    var QUEUE_ID = "toast-queue";
    var MAX_VISIBLE = 3;      // Au-dela, la plus ancienne alerte s'efface.
    var DURATION = 4500;      // Duree d'affichage d'une alerte simple.
    var STAGGER = 140;        // Decalage entre deux bannieres d'une meme rafale.

    var TITLES = {
        success: "C'est noté",
        error: "Action impossible",
        warning: "Attention",
        info: "Information",
    };

    // Pictogrammes (tracés Heroicons, trait de 1.8) : pas de dependance a
    // Iconify, dont le rendu asynchrone laisserait la bulle vide un instant.
    var ICONS = {
        success: '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>',
        error: '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m0 3.75h.008v.008H12v-.008ZM21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>',
        warning: '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"/>',
        info: '<path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z"/>',
    };
    var CLOSE_ICON = '<path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12"/>';

    function svg(inner) {
        return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            + 'width="18" height="18" aria-hidden="true" focusable="false">' + inner + "</svg>";
    }

    function layer() {
        var host = document.getElementById(LAYER_ID);
        if (host) { return host; }
        host = document.createElement("div");
        host.id = LAYER_ID;
        host.className = "toast-layer";
        host.setAttribute("role", "region");
        host.setAttribute("aria-label", "Alertes");
        host.setAttribute("aria-live", "polite");
        document.body.appendChild(host);
        return host;
    }

    function show(text, tone, title, duration) {
        if (!text) { return null; }
        tone = TITLES[tone] ? tone : "info";

        var host = layer();
        var el = document.createElement("div");
        el.className = "toast toast-" + tone;
        el.setAttribute("role", tone === "error" ? "alert" : "status");
        el.innerHTML =
            '<span class="toast-icon">' + svg(ICONS[tone]) + "</span>"
            + '<span class="toast-body"><span class="toast-title"></span>'
            + '<span class="toast-text"></span></span>'
            + '<button type="button" class="toast-close" aria-label="Fermer">'
            + svg(CLOSE_ICON) + "</button>"
            + '<span class="toast-bar"></span>';
        // textContent : le texte peut venir d'une saisie utilisateur.
        el.querySelector(".toast-title").textContent = title || TITLES[tone];
        el.querySelector(".toast-text").textContent = String(text);

        var life = duration || DURATION;
        el.querySelector(".toast-bar").style.animationDuration = life + "ms";
        var timer = setTimeout(dismiss, life);

        function dismiss() {
            if (el.getAttribute("data-closing")) { return; }
            el.setAttribute("data-closing", "1");
            clearTimeout(timer);
            el.classList.add("leaving");
            // Filet si l'animation est desactivee (ou jamais jouee) : l'element
            // doit partir de la page quand meme.
            setTimeout(function () { if (el.parentNode) { el.parentNode.removeChild(el); } }, 600);
        }
        el.dismiss = dismiss;

        host.appendChild(el);
        // iOS : un tap sur la banniere la referme.
        el.addEventListener("click", dismiss);

        Array.prototype.forEach.call(
            host.querySelectorAll(".toast:not([data-closing])"),
            function (other, index) {
                if (index >= MAX_VISIBLE && other.dismiss) { other.dismiss(); }
            }
        );
        return el;
    }

    function boot() {
        var queue = document.getElementById(QUEUE_ID);
        if (!queue) { return; }
        var items = queue.querySelectorAll("[data-toast]");
        Array.prototype.forEach.call(items, function (el, index) {
            // Les alertes d'une meme rafale arrivent decalees : elles s'empilent
            // l'une sous l'autre au lieu de se chevauiller.
            setTimeout(function () {
                show(
                    el.getAttribute("data-toast"),
                    el.getAttribute("data-toast-tone"),
                    el.getAttribute("data-toast-title") || ""
                );
            }, index * STAGGER);
        });
        if (queue.parentNode) { queue.parentNode.removeChild(queue); }
    }

    document.addEventListener("DOMContentLoaded", boot);

    window.toast = show;
    window.StkToast = {
        show: show,
        success: function (text, title) { return show(text, "success", title); },
        error: function (text, title) { return show(text, "error", title); },
        warning: function (text, title) { return show(text, "warning", title); },
        info: function (text, title) { return show(text, "info", title); },
    };
})();