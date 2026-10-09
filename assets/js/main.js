"use strict";

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
document.querySelectorAll("[data-year]").forEach((node) => {
  node.textContent = new Date().getFullYear();
});

function setupDialog(dialog) {
  if (!dialog) return () => {};
  dialog
    .querySelector(".dialog-close")
    .addEventListener("click", () => dialog.close());
  dialog.addEventListener("keydown", (event) => {
    if (event.key !== "Tab") return;
    const stops = [
      ...dialog.querySelectorAll(
        'a[href], button:not([disabled]), [tabindex="0"]',
      ),
    ].filter((node) => node.getClientRects().length);
    const first = stops[0],
      last = stops[stops.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
  dialog.addEventListener("click", (event) => {
    const bounds = dialog.getBoundingClientRect();
    if (
      event.target === dialog &&
      (event.clientX < bounds.left ||
        event.clientX > bounds.right ||
        event.clientY < bounds.top ||
        event.clientY > bounds.bottom)
    )
      dialog.close();
  });
  dialog.addEventListener("close", () => {
    document.body.classList.toggle(
      "modal-open",
      Boolean(document.querySelector("dialog[open]")),
    );
    window.dispatchEvent(new Event("modalchange"));
  });
  return () => {
    dialog.showModal();
    dialog.scrollTop = 0;
    document.body.classList.add("modal-open");
    window.dispatchEvent(new Event("modalchange"));
  };
}

function initPhotos() {
  const buttons = [...document.querySelectorAll("[data-photo]")];
  const dialog = document.querySelector("#photo-dialog");
  if (!buttons.length || !dialog) return;
  const open = setupDialog(dialog);
  let current = 0;
  function show(index) {
    current = (index + buttons.length) % buttons.length;
    const original = buttons[current].querySelector("img");
    const image = document.querySelector("#lightbox-image");
    image.src = original.src;
    image.alt = original.alt;
    document.querySelector("#lightbox-caption").textContent = original.alt;
    document.querySelector("#photo-count").textContent =
      current + 1 + " / " + buttons.length;
  }
  buttons.forEach((button, index) =>
    button.addEventListener("click", () => {
      show(index);
      open();
    }),
  );
  dialog
    .querySelector("[data-photo-prev]")
    .addEventListener("click", () => show(current - 1));
  dialog
    .querySelector("[data-photo-next]")
    .addEventListener("click", () => show(current + 1));
  dialog.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      show(current + (event.key === "ArrowLeft" ? -1 : 1));
    }
  });
  let start = null;
  const image = document.querySelector("#lightbox-image");
  image.addEventListener(
    "touchstart",
    (event) => {
      start = { x: event.touches[0].clientX, y: event.touches[0].clientY };
    },
    { passive: true },
  );
  image.addEventListener(
    "touchend",
    (event) => {
      if (!start) return;
      const dx = event.changedTouches[0].clientX - start.x;
      const dy = event.changedTouches[0].clientY - start.y;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy))
        show(current + (dx < 0 ? 1 : -1));
      start = null;
    },
    { passive: true },
  );
}

function initProjectMotion() {
  if (!window.IntersectionObserver || !Element.prototype.animate) return;
  const previews = [...document.querySelectorAll(".preview-image")];
  const motions = new Map();
  const visible = new Set();
  function sync() {
    motions.forEach((animation, image) => {
      if (reducedMotion.matches) {
        animation.cancel();
      } else if (
        visible.has(image) &&
        !document.hidden &&
        !document.body.classList.contains("modal-open")
      ) {
        animation.play();
      } else {
        animation.pause();
      }
    });
  }
  previews.forEach((image, index) => {
    const animation = image.animate(
      [
        { transform: "scale(1.04) translateY(0)" },
        { transform: "scale(1.08) translateY(-1%)" },
      ],
      {
        duration: 6500 + index * 1500,
        iterations: Infinity,
        direction: "alternate",
        easing: "ease-in-out",
      },
    );
    animation.pause();
    motions.set(image, animation);
  });
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(({ target, isIntersecting }) => {
      if (isIntersecting) visible.add(target);
      else visible.delete(target);
    });
    sync();
  });
  previews.forEach((image) => observer.observe(image));
  document.addEventListener("visibilitychange", sync);
  window.addEventListener("modalchange", sync);
  reducedMotion.addEventListener("change", sync);
  sync();
}

function initReveals() {
  if (!window.IntersectionObserver || !Element.prototype.animate) return;
  const animations = new Map();
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(({ target, isIntersecting }) => {
        if (!isIntersecting) return;
        observer.unobserve(target);
        if (reducedMotion.matches || target.contains(document.activeElement))
          return;
        const animation = target.animate(
          [
            { opacity: 0, transform: "translateY(16px)" },
            { opacity: 1, transform: "translateY(0)" },
          ],
          { duration: 650, easing: "cubic-bezier(.2,.7,.2,1)" },
        );
        animations.set(target, animation);
        animation.finished
          .then(() => animations.delete(target))
          .catch(() => animations.delete(target));
      });
    },
    { threshold: 0.05 },
  );
  document
    .querySelectorAll(
      ".intro, .personal-project, .note-section, .personal-photos, .gallery-grid .photo-button",
    )
    .forEach((node) => observer.observe(node));
  document.addEventListener("focusin", (event) => {
    animations.forEach((animation, target) => {
      if (target.contains(event.target)) animation.cancel();
    });
  });
  reducedMotion.addEventListener("change", () => {
    if (reducedMotion.matches)
      animations.forEach((animation) => animation.cancel());
  });
}

initPhotos();
initProjectMotion();
initReveals();
if (typeof initAfterglow === "function") initAfterglow();
