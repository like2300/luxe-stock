/* Bips des notifications — Web Audio API, aucun fichier son à fournir.
   Chaque code son correspond à une fréquence et à un nombre de bips. */
(function () {
  "use strict";

  var SEQUENCES = {
    AJOUT: [880, 1175],
    ENTREE: [660, 880],
    SORTIE: [440, 330],
    BAS: [523, 523, 392],
    RUPTURE: [294, 294, 294, 220],
    AJUST: [740, 622, 740]
  };

  var DEFAULT_SEQUENCE = [880];
  var enabled = true;

  function beep(freq, delay) {
    var Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    var ctx = beep.ctx || (beep.ctx = new Ctx());
    if (ctx.state === "suspended") ctx.resume();

    var osc = ctx.createOscillator();
    var gain = ctx.createGain();
    var start = ctx.currentTime + delay;

    osc.type = "sine";
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(0.0001, start);
    gain.gain.exponentialRampToValueAtTime(0.22, start + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.22);

    osc.connect(gain).connect(ctx.destination);
    osc.start(start);
    osc.stop(start + 0.25);
  }

  function isEnabled() {
    // Priorité : interrupteur global du header (par PC, localStorage).
    if (window.StockSound && typeof window.StockSound.isEnabled === "function") {
      return window.StockSound.isEnabled();
    }
    return enabled;
  }

  function play(code, tone) {
    if (!isEnabled()) return;
    var seq = SEQUENCES[code];
    if (!seq) {
      seq = tone ? [tone] : DEFAULT_SEQUENCE;
      beep(seq[0], 0);
      return;
    }
    seq.forEach(function (f, i) {
      beep(f, i * 0.26);
    });
  }

  // Les navigateurs bloquent l'audio tant que l'utilisateur n'a pas interagi :
  // on débloque le contexte au premier clic.
  document.addEventListener("click", function once() {
    var Ctx = window.AudioContext || window.webkitAudioContext;
    if (Ctx && !beep.ctx) {
      beep.ctx = new Ctx();
      beep.ctx.resume();
    }
    document.removeEventListener("click", once);
  });

  document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("sound-toggle");
    if (toggle) {
      // L'état vient du header (localStorage par PC). Les anciens
      // interrupteurs de type checkbox restent compatibles.
      if (toggle.type === "checkbox") {
        enabled = toggle.checked;
        toggle.addEventListener("change", function () {
          enabled = toggle.checked;
          if (enabled) play("AJOUT");
        });
      }
    }

    var test = document.getElementById("sound-test");
    if (test) test.addEventListener("click", function () { play("AJOUT"); });

    document.querySelectorAll("button.play, .code-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        play(btn.dataset.code, parseInt(btn.dataset.tone, 10));
      });
    });

    // Lecture du bip de chaque nouvelle notification, à l'arrivée sur la page.
    if (document.querySelector("tr.notif.unread")) {
      var codes = [].slice
        .call(document.querySelectorAll("tr.notif.unread"))
        .slice(0, 5)
        .map(function (row) { return row.dataset.sound; });
      if (codes.length) {
        codes.forEach(function (c, i) { setTimeout(function () { play(c); }, i * 700); });
      }
    }
  });

  window.playNotificationSound = play;
  // Petit bip de confirmation pour l'appui sur un bouton de l'interface.
  window.previewUiSound = function () { beep(DEFAULT_SEQUENCE[0], 0); };
})();
