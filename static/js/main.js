/* ── THEME ───────────────────────────────────────────────── */
(function () {
  const saved = localStorage.getItem("theme") || "light";
  applyTheme(saved, false);
})();

function applyTheme(theme, save = true) {
  document.documentElement.setAttribute("data-theme", theme);
  if (save) localStorage.setItem("theme", theme);
  const icon  = document.getElementById("theme-icon");
  const label = document.getElementById("theme-label");
  if (icon)  icon.textContent  = theme === "dark" ? "🌙" : "☀️";
  if (label) label.textContent = theme === "dark" ? "Dark" : "Light";
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  applyTheme(current === "dark" ? "light" : "dark");
}

/* ── SIDEBAR TOGGLE (mobile) ─────────────────────────────── */
function toggleSidebar() {
  const sidebar = document.querySelector(".sidebar");
  if (sidebar) sidebar.classList.toggle("sidebar-open");
}

/* ── AUTO-DISMISS FLASH MESSAGES ────────────────────────── */
document.addEventListener("DOMContentLoaded", function () {
  setTimeout(() => {
    document.querySelectorAll(".alert.fade.show").forEach(el => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    });
  }, 4000);
});
