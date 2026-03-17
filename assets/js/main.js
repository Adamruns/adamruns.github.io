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

function initScrollAnimations() {
  const elements = document.querySelectorAll(".fade-in");

  if (!elements.length) return;

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  elements.forEach(function (element) {
    observer.observe(element);
  });
}

function initThemeToggle() {
  const toggle = document.querySelector(".theme-toggle");

  if (!toggle) return;

  const storedTheme = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = storedTheme || (prefersDark ? "dark" : "light");

  document.documentElement.setAttribute("data-theme", theme);

  toggle.addEventListener("click", function () {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const nextTheme = currentTheme === "dark" ? "light" : "dark";

    document.documentElement.setAttribute("data-theme", nextTheme);
    localStorage.setItem("theme", nextTheme);
  });
}

function initLightbox() {
  const grid = document.querySelector(".photo-grid");

  if (!grid) return;

  var lightbox = document.createElement("div");
  lightbox.className = "lightbox";
  lightbox.innerHTML = '<button class="lightbox-close" aria-label="Close">&times;</button><img src="" alt="">';
  document.body.appendChild(lightbox);

  var lightboxImage = lightbox.querySelector("img");
  var closeButton = lightbox.querySelector(".lightbox-close");

  function openLightbox(source, altText) {
    lightboxImage.src = source;
    lightboxImage.alt = altText;
    lightbox.classList.add("active");
    document.body.style.overflow = "hidden";
  }

  function closeLightbox() {
    lightbox.classList.remove("active");
    document.body.style.overflow = "";
  }

  grid.addEventListener("click", function (event) {
    if (event.target.tagName === "IMG") {
      openLightbox(event.target.src, event.target.alt);
    }
  });

  closeButton.addEventListener("click", closeLightbox);

  lightbox.addEventListener("click", function (event) {
    if (event.target === lightbox) {
      closeLightbox();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && lightbox.classList.contains("active")) {
      closeLightbox();
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  initNavToggle();
  initScrollAnimations();
  initThemeToggle();
  initLightbox();
});
