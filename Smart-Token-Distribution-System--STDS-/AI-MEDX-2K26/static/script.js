/* ── script.js  ─────────────────────────────────────────────────────────────
   Handles:
   1. Splash screen → redirect to login after 2 s
   2. Input auto-formatting
   3. Subtle ripple effect on buttons
   ─────────────────────────────────────────────────────────────────────────── */

(function () {
  "use strict";

  /* ── 1. Splash screen redirect ─────────────────────────────────────────── */
  const splashScreen = document.getElementById("splashScreen");
  if (splashScreen) {
    // 2 s for splash display, then 0.7 s fade (matches CSS), then redirect
    setTimeout(function () {
      window.location.href = "/";
    }, 2900);
  }

  /* ── 2. Token digit input — only allow numbers ─────────────────────────── */
  document.querySelectorAll('input[name="token"]').forEach(function (input) {
    input.addEventListener("input", function () {
      this.value = this.value.replace(/\D/g, "").slice(0, 6);
    });
  });

  /* ── 3. Phone number input — only allow digits, spaces, + ─────────────── */
  document.querySelectorAll('input[type="tel"]').forEach(function (input) {
    input.addEventListener("input", function () {
      this.value = this.value.replace(/[^0-9+\- ]/g, "");
    });
  });

  /* ── 4. Ripple effect on all buttons ──────────────────────────────────── */
  document.addEventListener("click", function (e) {
    const btn = e.target.closest(".btn");
    if (!btn) return;

    const circle = document.createElement("span");
    const diameter = Math.max(btn.clientWidth, btn.clientHeight);
    const rect = btn.getBoundingClientRect();

    circle.style.cssText = [
      "position:absolute",
      "border-radius:50%",
      "background:rgba(255,255,255,0.35)",
      "pointer-events:none",
      "transform:scale(0)",
      "animation:ripple 0.55s linear",
      `width:${diameter}px`,
      `height:${diameter}px`,
      `left:${e.clientX - rect.left - diameter / 2}px`,
      `top:${e.clientY - rect.top - diameter / 2}px`,
    ].join(";");

    // Ensure btn is positioned for the ripple
    const prevPos = getComputedStyle(btn).position;
    if (prevPos === "static") btn.style.position = "relative";
    btn.style.overflow = "hidden";
    btn.appendChild(circle);

    circle.addEventListener("animationend", function () {
      circle.remove();
    });
  });

  // Inject ripple keyframes once
  if (!document.getElementById("rippleStyle")) {
    const style = document.createElement("style");
    style.id = "rippleStyle";
    style.textContent =
      "@keyframes ripple { to { transform: scale(2.5); opacity: 0; } }";
    document.head.appendChild(style);
  }

  /* ── 5. Auto-dismiss alerts after 4 s ─────────────────────────────────── */
  document.querySelectorAll(".alert").forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = "opacity 0.5s";
      alert.style.opacity = "0";
      setTimeout(function () { alert.remove(); }, 500);
    }, 4000);
  });

  /* ── 6. Token number copy on click (result page) ──────────────────────── */
  const tokenEl = document.getElementById("tokenNumber");
  if (tokenEl) {
    tokenEl.title = "Click to copy";
    tokenEl.style.cursor = "pointer";
    tokenEl.addEventListener("click", function () {
      navigator.clipboard.writeText(tokenEl.textContent.trim()).then(function () {
        const original = tokenEl.textContent;
        tokenEl.textContent = "Copied!";
        tokenEl.style.fontSize = "1.6rem";
        setTimeout(function () {
          tokenEl.textContent = original;
          tokenEl.style.fontSize = "";
        }, 1200);
      }).catch(function () { });
    });
  }

})();
