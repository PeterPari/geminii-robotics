/* GEMINII behavior. No dependencies. Progressive enhancement: the site works without it.
   Hooks (data attributes):
     [data-gm-theme-toggle]                 button; cycles light and dark, remembers the choice
     [data-gm-nav-toggle="menu-id"]         button; opens and closes the menu with that id
     [data-gm-tabs] > [role=tablist]        tabs with arrow, Home and End keys
*/
(function () {
  "use strict";

  /* ---------------------------------------------------------------- theme */
  function currentTheme() {
    var attr = document.documentElement.getAttribute("data-theme");
    if (attr === "light" || attr === "dark") return attr;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem("gm-theme", theme); } catch (e) { /* ignore */ }
    document.querySelectorAll("[data-gm-theme-toggle]").forEach(function (b) {
      b.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    });
    document.dispatchEvent(new CustomEvent("gm:theme", { detail: { theme: theme } }));
  }

  document.querySelectorAll("[data-gm-theme-toggle]").forEach(function (btn) {
    btn.setAttribute("aria-pressed", currentTheme() === "dark" ? "true" : "false");
    btn.addEventListener("click", function () { setTheme(currentTheme() === "dark" ? "light" : "dark"); });
  });

  /* ---------------------------------------------------------------- nav */
  document.querySelectorAll("[data-gm-nav-toggle]").forEach(function (btn) {
    var menu = document.getElementById(btn.getAttribute("data-gm-nav-toggle"));
    if (!menu) return;
    function set(open) {
      menu.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    }
    set(false);
    btn.addEventListener("click", function () { set(btn.getAttribute("aria-expanded") !== "true"); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && btn.getAttribute("aria-expanded") === "true") { set(false); btn.focus(); }
    });
    if (window.matchMedia) {
      window.matchMedia("(min-width: 960px)").addEventListener("change", function (e) { if (e.matches) set(false); });
    }
  });

  /* ---------------------------------------------------------------- tabs */
  document.querySelectorAll("[data-gm-tabs]").forEach(function (root) {
    var tabs = Array.prototype.slice.call(root.querySelectorAll('[role="tab"]'));
    if (!tabs.length) return;
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.setAttribute("tabindex", on ? "0" : "-1");
        var panel = document.getElementById(t.getAttribute("aria-controls"));
        if (panel) panel.hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { select(tab, false); });
      tab.addEventListener("keydown", function (e) {
        var n = tabs.length, next = null;
        if (e.key === "ArrowRight") next = tabs[(i + 1) % n];
        else if (e.key === "ArrowLeft") next = tabs[(i - 1 + n) % n];
        else if (e.key === "Home") next = tabs[0];
        else if (e.key === "End") next = tabs[n - 1];
        if (next) { e.preventDefault(); select(next, true); }
      });
    });
    var initial = tabs.filter(function (t) { return t.getAttribute("aria-selected") === "true"; })[0] || tabs[0];
    select(initial, false);
  });
})();
