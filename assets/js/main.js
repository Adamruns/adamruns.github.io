"use strict";

const ACTIVITY_DAY_MILLISECONDS = 24 * 60 * 60 * 1000;
const ACTIVITY_DATE_FORMAT = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  timeZone: "UTC",
});
const ACTIVITY_MONTH_FORMAT = new Intl.DateTimeFormat("en-US", {
  month: "short",
  timeZone: "UTC",
});
const ACTIVITY_UPDATED_FORMAT = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
});
const NUMBER_FORMAT = new Intl.NumberFormat("en-US");

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

function activityLevelThresholds(counts) {
  const activeCounts = counts
    .filter((count) => count > 0)
    .sort((first, second) => first - second);
  return [0.25, 0.5, 0.75].map(
    (quantile) =>
      activeCounts[Math.floor(quantile * (activeCounts.length - 1))] ?? 0,
  );
}

function renderActivity(container, activity) {
  const startTime = Date.parse(`${activity.start}T00:00:00Z`);
  const firstWeekday = new Date(startTime).getUTCDay();
  const weekCount = Math.ceil((firstWeekday + activity.counts.length) / 7);
  const thresholds = activityLevelThresholds(activity.counts);
  const activeDays = activity.counts.filter((count) => count > 0).length;
  const grid = container.querySelector(".activity-grid");
  const months = container.querySelector(".activity-months");
  const monthLabels = [];
  let previousMonth = null;

  activity.counts.forEach((count, index) => {
    const date = new Date(startTime + index * ACTIVITY_DAY_MILLISECONDS);
    const cell = document.createElement("span");
    cell.dataset.level = count
      ? 1 + thresholds.filter((threshold) => count > threshold).length
      : 0;
    cell.title = `${NUMBER_FORMAT.format(count)} ${count === 1 ? "contribution" : "contributions"} on ${ACTIVITY_DATE_FORMAT.format(date)}`;
    if (index === 0) cell.style.gridRowStart = firstWeekday + 1;
    grid.append(cell);

    const position = firstWeekday + index;
    if (index > 0 && position % 7 !== 0) return;

    if (date.getUTCMonth() !== previousMonth) {
      monthLabels.push({
        column: Math.floor(position / 7) + 1,
        text: ACTIVITY_MONTH_FORMAT.format(date),
      });
    }
    previousMonth = date.getUTCMonth();
  });

  // A partial first month would print its label on top of the next one.
  if (monthLabels.length > 1 && monthLabels[1].column - monthLabels[0].column < 3)
    monthLabels.shift();
  monthLabels.forEach(({ column, text }) => {
    const label = document.createElement("span");
    label.textContent = text;
    label.style.gridColumnStart = column;
    months.append(label);
  });

  grid.style.setProperty("--activity-weeks", weekCount);
  months.style.setProperty("--activity-weeks", weekCount);
  const total = NUMBER_FORMAT.format(activity.total);
  const days = NUMBER_FORMAT.format(activeDays);
  grid.setAttribute(
    "aria-label",
    `${total} contributions in the past year, on ${days} different days`,
  );
  container
    .querySelector("[data-activity-summary]")
    .replaceChildren(
      Object.assign(document.createElement("strong"), { textContent: total }),
      " contributions in the past year, on ",
      Object.assign(document.createElement("strong"), { textContent: days }),
      " different days.",
    );
  container.querySelector("[data-activity-updated]").textContent =
    `Updated ${ACTIVITY_UPDATED_FORMAT.format(new Date(activity.updated))}`;
  const scroller = container.querySelector(".activity-scroll");
  scroller.scrollLeft = scroller.scrollWidth;
}

function initActivity() {
  const container = document.querySelector("[data-activity-source]");
  if (!container) return;
  fetch(container.dataset.activitySource)
    .then((response) => {
      if (!response.ok)
        throw new Error(`Activity request failed with ${response.status}`);
      return response.json();
    })
    .then((activity) => renderActivity(container, activity))
    .catch(() => {
      container.classList.add("activity-unavailable");
      container.querySelector("[data-activity-summary]").textContent =
        "The contribution calendar didn’t load. You can still see it on GitHub.";
    });
}

initPhotos();
initMenu();
initActivity();
if (typeof initAfterglow === "function") initAfterglow();
