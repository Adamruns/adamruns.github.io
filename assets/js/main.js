function initNavToggle() {
  const toggle = document.querySelector(".nav-toggle");
  const navLinks = document.querySelector(".nav-links");

  if (!toggle || !navLinks) return;

  toggle.addEventListener("click", function () {
    const isOpen = navLinks.classList.toggle("nav-links--open");
    toggle.classList.toggle("nav-toggle--open", isOpen);
    toggle.setAttribute("aria-expanded", isOpen);
  });

  navLinks.addEventListener("click", function (event) {
    if (event.target.tagName === "A") {
      navLinks.classList.remove("nav-links--open");
      toggle.classList.remove("nav-toggle--open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });
}

document.addEventListener("DOMContentLoaded", initNavToggle);
