"use strict";

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

function initMenu() {
  const header = document.querySelector(".site-header");
  const button = header?.querySelector(".menu-button");
  if (!button) return;
  function setOpen(open) {
    button.setAttribute("aria-expanded", String(open));
    header.toggleAttribute("data-menu-open", open);
  }
  button.addEventListener("click", () =>
    setOpen(button.getAttribute("aria-expanded") !== "true"),
  );
  header
    .querySelectorAll(".site-nav a")
    .forEach((link) => link.addEventListener("click", () => setOpen(false)));
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !header.hasAttribute("data-menu-open"))
      return;
    setOpen(false);
    button.focus();
  });
  document.addEventListener("click", (event) => {
    if (!header.contains(event.target)) setOpen(false);
  });
  window
    .matchMedia("(min-width: 761px)")
    .addEventListener("change", () => setOpen(false));
}

initPhotos();
initMenu();
if (typeof initAfterglow === "function") initAfterglow();
