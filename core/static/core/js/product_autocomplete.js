(function () {
    "use strict";

    var DEBOUNCE_MS = 200;
    var MIN_CHARS = 1;
    var MAX_CHARS = 60;

    function escapeHtml(value) {
        return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
        });
    }

    function stockBadge(item, kind) {
        var n = Number(item.stock) || 0;
        if (kind === "category") {
            var libelle = n > 1 ? "produits" : "produit";
            return '<span class="ml-auto shrink-0 text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">' + n + " " + libelle + "</span>";
        }
        if (item.badge) {
            return '<span class="ml-auto shrink-0 text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">' + n + " " + escapeHtml(item.badge) + "</span>";
        }
        var cls = n > 0 ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700";
        return '<span class="ml-auto shrink-0 text-[11px] font-medium px-2 py-0.5 rounded-full ' + cls + '">' + n + " en stock</span>";
    }

    function Autocomplete(root) {
        this.root = root;
        this.input = root.querySelector('[data-role="search"]');
        this.listbox = root.querySelector('[data-role="listbox"]');
        this.status = root.querySelector('[data-role="status"]');
        this.clearBtn = root.querySelector('[data-role="clear"]');
        this.fallback = root.querySelector('[data-role="fallback"]');
        this.select = root.querySelector("select");
        this.endpoint = this.input.getAttribute("data-endpoint");
        this.kind = root.getAttribute("data-kind") || "product";
        this.timer = null;
        this.controller = null;
        this.items = [];
        this.active = -1;

        this.init();
    }

    Autocomplete.prototype.init = function () {
        var self = this;

        if (this.select && this.select.value) {
            this.setText(this.selectedText(), true);
        }

        this.input.addEventListener("input", function () {
            self.onInput();
        });

        this.input.addEventListener("keydown", function (event) {
            self.onKeyDown(event);
        });

        this.clearBtn.addEventListener("click", function () {
            self.reset();
            self.input.focus();
        });

        this.listbox.addEventListener("mousedown", function (event) {
            // mousedown avant le blur : empeche la fermeture premature de la liste
            var option = event.target.closest("[data-index]");
            if (!option) {
                return;
            }
            event.preventDefault();
            self.choose(Number(option.getAttribute("data-index")));
        });

        document.addEventListener("click", function (event) {
            if (!self.root.contains(event.target)) {
                self.closeList();
            }
        });

        this.input.addEventListener("blur", function () {
            window.setTimeout(function () {
                self.closeList();
            }, 120);
        });

        var form = this.root.closest("form");
        if (form) {
            form.addEventListener("submit", function () {
                if (self.select && !self.select.value && self.fallback) {
                    self.fallback.open = true;
                }
            });
        }

        if (this.select) {
            this.select.addEventListener("change", function () {
                self.setText(self.selectedText(), true);
            });
        }
    };

    Autocomplete.prototype.selectedText = function () {
        if (!this.select || !this.select.value) {
            return "";
        }
        var option = this.select.options[this.select.selectedIndex];
        return option ? option.textContent.trim() : "";
    };

    Autocomplete.prototype.setText = function (text, syncInput) {
        if (syncInput) {
            this.input.value = text;
        }
        if (this.clearBtn) {
            this.clearBtn.classList.toggle("hidden", !text);
        }
    };

    Autocomplete.prototype.onInput = function () {
        var self = this;
        var query = this.input.value.trim().slice(0, MAX_CHARS);

        if (this.clearBtn) {
            this.clearBtn.classList.toggle("hidden", !this.input.value);
        }

        window.clearTimeout(this.timer);
        if (query.length < MIN_CHARS) {
            this.abort();
            this.closeList();
            this.setStatus("");
            return;
        }

        this.timer = window.setTimeout(function () {
            self.fetchSuggestions(query);
        }, DEBOUNCE_MS);
    };

    Autocomplete.prototype.abort = function () {
        if (this.controller) {
            this.controller.abort();
            this.controller = null;
        }
    };

    Autocomplete.prototype.fetchSuggestions = function (query) {
        var self = this;
        this.abort();
        if (window.AbortController) {
            this.controller = new AbortController();
        }
        this.setStatus("Recherche en cours...");

        var options = { headers: { "X-Requested-With": "XMLHttpRequest" } };
        if (this.controller) {
            options.signal = this.controller.signal;
        }

        fetch(this.endpoint + "?q=" + encodeURIComponent(query), options)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("HTTP " + response.status);
                }
                return response.json();
            })
            .then(function (data) {
                self.render(data.results || []);
            })
            .catch(function (error) {
                if (error.name === "AbortError") {
                    return;
                }
                self.items = [];
                self.closeList();
                self.setStatus("Recherche impossible pour le moment.");
            });
    };

    Autocomplete.prototype.render = function (results) {
        var self = this;
        this.items = results;
        this.active = results.length ? 0 : -1;

        if (!results.length) {
            this.closeList();
            this.setStatus("Aucun résultat.");
            return;
        }

        var html = results
            .map(function (item, index) {
                var meta = [item.sku, item.category].filter(Boolean).join(" - ");
                return (
                    '<li id="product-option-' + index + '" role="option" data-index="' + index + '" aria-selected="false"' +
                    ' class="flex items-center gap-3 px-4 py-2.5 cursor-pointer text-sm text-slate-600 hover:bg-slate-50 hover:text-primary transition-colors">' +
                    '<span class="font-medium truncate">' + escapeHtml(item.name) + "</span>" +
                    (meta ? '<span class="text-xs text-slate-400 truncate">' + escapeHtml(meta) + "</span>" : "") +
                    stockBadge(item, self.kind) +
                    "</li>"
                );
            })
            .join("");

        this.listbox.innerHTML = html;
        this.listbox.classList.remove("hidden");
        this.input.setAttribute("aria-expanded", "true");
        var mot = this.kind === "category" ? "catégorie" : "produit";
        this.setStatus(results.length + " " + mot + (results.length > 1 ? "s" : "") + " trouvé(s).");
        this.highlight();
    };

    Autocomplete.prototype.highlight = function () {
        var options = this.listbox.querySelectorAll("[data-index]");
        for (var i = 0; i < options.length; i++) {
            var on = i === this.active;
            options[i].classList.toggle("bg-slate-50", on);
            options[i].classList.toggle("text-primary", on);
            options[i].setAttribute("aria-selected", on ? "true" : "false");
        }
        if (this.active >= 0 && options[this.active]) {
            this.input.setAttribute("aria-activedescendant", options[this.active].id);
            if (options[this.active].scrollIntoView) {
                options[this.active].scrollIntoView({ block: "nearest" });
            }
        } else {
            this.input.removeAttribute("aria-activedescendant");
        }
    };

    Autocomplete.prototype.closeList = function () {
        this.listbox.classList.add("hidden");
        this.listbox.innerHTML = "";
        this.input.setAttribute("aria-expanded", "false");
        this.input.removeAttribute("aria-activedescendant");
        this.items = [];
        this.active = -1;
    };

    Autocomplete.prototype.setStatus = function (text) {
        if (this.status) {
            this.status.textContent = text;
        }
    };

    Autocomplete.prototype.onKeyDown = function (event) {
        var count = this.items.length;

        if (event.key === "ArrowDown" && count) {
            event.preventDefault();
            this.active = (this.active + 1) % count;
            this.highlight();
        } else if (event.key === "ArrowUp" && count) {
            event.preventDefault();
            this.active = (this.active - 1 + count) % count;
            this.highlight();
        } else if (event.key === "Enter") {
            if (count && !this.listbox.classList.contains("hidden")) {
                event.preventDefault();
                this.choose(this.active);
            }
        } else if (event.key === "Escape") {
            if (count) {
                event.preventDefault();
                this.closeList();
            }
        } else if (event.key === "Tab" && !this.listbox.classList.contains("hidden")) {
            this.closeList();
        }
    };

    Autocomplete.prototype.choose = function (index) {
        var item = this.items[index];
        if (!item || !this.select) {
            return;
        }
        this.select.value = String(item.id);
        this.select.dispatchEvent(new Event("change", { bubbles: true }));
        this.input.value = item.name;
        if (this.clearBtn) {
            this.clearBtn.classList.remove("hidden");
        }
        this.closeList();
        this.setStatus("Choisi : " + item.name);
    };

    Autocomplete.prototype.reset = function () {
        this.abort();
        window.clearTimeout(this.timer);
        if (this.select) {
            this.select.value = "";
            this.select.dispatchEvent(new Event("change", { bubbles: true }));
        }
        this.input.value = "";
        if (this.clearBtn) {
            this.clearBtn.classList.add("hidden");
        }
        this.closeList();
        this.setStatus("");
    };

    function boot() {
        var roots = document.querySelectorAll("[data-product-autocomplete]");
        for (var i = 0; i < roots.length; i++) {
            new Autocomplete(roots[i]);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }

    window.ProductAutocomplete = Autocomplete;
})();