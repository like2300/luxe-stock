/* Suggestions automatiques des barres de recherche — dropdown + navigation clavier. */
(function () {
  "use strict";

  function closeAll(except) {
    document.querySelectorAll(".suggest-box").forEach(function (box) {
      if (box !== except) box.remove();
    });
  }

  function bind(input) {
    var url = input.dataset.suggestUrl;
    if (!url || input.dataset.suggestBound) return;
    input.dataset.suggestBound = "1";
    input.setAttribute("autocomplete", "off");

    var box = null;
    var active = -1;
    var timer = null;

    function render(items) {
      closeAll();
      active = -1;
      if (!items.length) return;
      box = document.createElement("div");
      box.className = "suggest-box";
      items.forEach(function (it, i) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "suggest-item";
        b.innerHTML =
          '<span class="suggest-label"></span>' +
          (it.sub ? '<span class="suggest-sub"></span>' : "");
        b.querySelector(".suggest-label").textContent = it.label;
        if (it.sub) b.querySelector(".suggest-sub").textContent = it.sub;
        b.addEventListener("mousedown", function (e) {
          e.preventDefault();
          input.value = it.value;
          closeAll();
          var form = input.closest("form");
          if (form && input.dataset.suggestSubmit !== "0") form.submit();
          else {
            input.dispatchEvent(new Event("input", { bubbles: true }));
            // Signale aux scripts de page qu'un choix vient d'être fait :
            // ils peuvent réagir immédiatement (ex. filtrage de la liste).
            input.dispatchEvent(new Event("suggest:chosen", { bubbles: true }));
          }
        });
        box.appendChild(b);
      });
      var wrap = input.parentElement;
      if (getComputedStyle(wrap).position === "static") wrap.style.position = "relative";
      wrap.appendChild(box);
    }

    function loadSuggestions() {
      var q = input.value.trim();
      // window.fetch explicite : une fonction locale nommée « fetch » masquerait
      // l'API et provoquerait une récursion infinie.
      window
        .fetch(url + "?q=" + encodeURIComponent(q), { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(function (r) { return r.json(); })
        .then(function (d) { render(d.results || []); })
        .catch(function () {});
    }

    input.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(loadSuggestions, 200);
    });
    input.addEventListener("focus", loadSuggestions);
    input.addEventListener("blur", function () { setTimeout(closeAll, 150); });
    input.addEventListener("keydown", function (e) {
      if (!box) return;
      var items = box.querySelectorAll(".suggest-item");
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        active = e.key === "ArrowDown" ? Math.min(active + 1, items.length - 1) : Math.max(active - 1, 0);
        items.forEach(function (b, i) { b.classList.toggle("active", i === active); });
        if (items[active]) items[active].scrollIntoView({ block: "nearest" });
      } else if (e.key === "Enter" && active >= 0 && items[active]) {
        e.preventDefault();
        items[active].dispatchEvent(new Event("mousedown"));
      } else if (e.key === "Escape") {
        closeAll();
      }
    });
  }

  function init() {
    document.querySelectorAll("input[data-suggest-url]").forEach(bind);
  }

  document.addEventListener("DOMContentLoaded", init);
  window.bindSuggest = bind;
})();
