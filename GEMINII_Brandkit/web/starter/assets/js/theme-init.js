/* GEMINII theme init. Load synchronously in <head>, before the stylesheet, so there is no flash of the wrong theme.
   - adds the "js" class (CSS uses it to collapse the mobile menu)
   - applies a saved theme ("light" or "dark") from localStorage; no saved value follows the system setting */
(function () {
  var root = document.documentElement;
  root.classList.add("js");
  try {
    var saved = localStorage.getItem("gm-theme");
    if (saved === "light" || saved === "dark") root.setAttribute("data-theme", saved);
  } catch (e) { /* storage blocked: follow the system setting */ }
})();
