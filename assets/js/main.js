"use strict";

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
document.querySelectorAll("[data-year]").forEach((node) => {
  node.textContent = new Date().getFullYear();
});

function initNavigation() {
  const toggle = document.querySelector(".menu-toggle");
  const menu = document.querySelector("#mobile-menu");
  if (!toggle || !menu) return;
  function close(returnFocus = false) {
    menu.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open navigation");
    if (returnFocus) toggle.focus();
  }
  toggle.addEventListener("click", () => {
    const open = toggle.getAttribute("aria-expanded") !== "true";
    menu.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute(
      "aria-label",
      open ? "Close navigation" : "Open navigation",
    );
  });
  menu.addEventListener("click", (event) => {
    if (event.target.closest("a")) close();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !menu.hidden) close(true);
  });
  document.addEventListener("click", (event) => {
    if (!menu.hidden && !event.target.closest(".site-header")) close();
  });
  window
    .matchMedia("(min-width: 761px)")
    .addEventListener("change", (event) => {
      if (event.matches) close();
    });
}

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

const caseStudies = {
  commerce: {
    category: "INDEPENDENT BUILD / COMMERCE & OPERATIONS",
    title: "Build the storefront.<br>Own the rest of it.",
    body: '<p class="case-lead">An end-to-end commerce platform I built for a research-material business, including the storefront and the operational tools behind it.</p><h3>Customer-facing work</h3><p>Product pages, a persistent cart, account creation and sign-in, and a three-step order-request flow: shipping, payment instructions, then review. Customers can look up an order with its order number and matching email address.</p><h3>What happens on the server</h3><ul><li>Resolve prices from the database rather than trusting the amounts submitted by the browser.</li><li>Check inventory during order creation and associate the order with the signed-in customer.</li><li>Store salted password hashes and use signed, HttpOnly session cookies.</li><li>Record confirmation emails in an outbox so delivery can be retried.</li><li>Give the operator tools for product edits, stock adjustments, requests, and sales records.</li></ul><h3>The architecture</h3><p>A Cloudflare Worker serves the storefront and admin routes, with D1 for application data. Separate preview and demo databases keep testing away from the production records.</p><p class="case-note">Built and awaiting its first customers. No customer traction or revenue results yet. Checkout records an order request and provides manual payment instructions; an automated payment processor is not connected.</p>',
  },
  smith: {
    category: "SMITH & SHIN CPAs / WEB OWNERSHIP",
    title: "The launch is<br>only part of the job.",
    body: '<p class="case-lead">I built and run the website for Smith &amp; Shin CPAs in Taylors, South Carolina.</p><h3>What I own</h3><p>The public site, the domain move, DNS configuration, and hosting. I transferred smithandshin.com from its previous registrar to Cloudflare and built the site on Cloudflare Pages, with deployment connected to the repository.</p><h3>The implementation</h3><p>A static HTML site with responsive layouts, service information, tax tips, staff profiles, and direct contact details. The project needs to help prospective clients understand the firm and find the next step.</p><h3>The engineering choice</h3><p>The content does not require a database or an application server. Static hosting keeps the deployment small and the maintenance straightforward. Running it also means owning the details that survive the design handoff: domain settings, navigation, and future updates.</p><div class="case-links"><a class="text-link" href="https://smithandshin.com" target="_blank" rel="noopener">Visit Smith &amp; Shin ↗</a></div>',
  },
  funding: {
    category: "MEDSHIFT / FINANCIAL SYSTEMS",
    title: "The whole system.<br>The details, too.",
    body: '<p class="case-lead">I built and own the Buy Side disbursement workflow at Velocity Lending, from funding operations through accounting integration.</p><h3>The problem</h3><p>A manual finance process relied on spreadsheets, email, and repeated handoffs. The work needed to scale while preserving the accounting details that make a financial system trustworthy.</p><h3>What I built</h3><p>A Python/Django funding pipeline with Vue interfaces and third-party integrations. I authored the original Buy Side workflow and the QuickBooks Online integration, connecting the operational process to posted invoices.</p><ul><li>Repeatable processing and reconciliation for the funding lifecycle.</li><li>Financial API integrations and automated document collection.</li><li>Backend, customer-facing, and internal admin features delivered together.</li></ul><h3>The result</h3><p>By July 2026, the system recorded <strong>$119.6M across 1,087 funded applications</strong>. The QuickBooks integration accounted for <strong>$31.0M in posted invoices</strong>. The automated workflow saves hundreds of hours of manual work annually.</p><p class="case-note">Volume figures are a July 10, 2026 snapshot. Recorded funded volume includes historical funding events backfilled into the system; it is not a claim of revenue generated or entirely new originations.</p>',
  },
  ai: {
    category: "MEDSHIFT / DEVELOPER EXPERIENCE",
    title: "Better tools.<br>Shared judgment.",
    body: '<p class="case-lead">I helped turn individual AI-tool adoption into a repeatable engineering workflow for the department.</p><h3>The problem</h3><p>A coding assistant is only as useful as its understanding of the codebase. Without shared context, it is easy to get plausible code that misses the architecture, conventions, or tests.</p><h3>What I changed</h3><ul><li>Authored repository-level agent instructions describing architecture, coding style, and test conventions.</li><li>Built reusable review and pre-PR checks so the same standards carry across changes.</li><li>Shipped an AI-assisted PR-review pipeline that surfaces findings while keeping engineers responsible for decisions.</li><li>Built MCP integrations to connect AI tools to useful application context.</li></ul><h3>My own engineering practice</h3><p>I passed <strong>1,000 merged PRs in July 2026</strong> and reviewed <strong>1,572 teammates’ pull requests</strong> in the recorded period. Treating recurring review feedback as something to learn from helped me build better checks before opening my own PRs.</p><p class="case-note">PR figures are historical milestones and a July 2026 snapshot, not live counters or a claim that AI alone caused the results.</p>',
  },
  iroar: {
    category: "PERSONAL / CHROME EXTENSION",
    title: "Make the information<br>meet the decision.",
    body: '<p class="case-lead">iRoar Premium brings professor ratings and historical grade distributions into Clemson’s course planner.</p><h3>The idea</h3><p>Choosing classes meant jumping between a registration page, professor reviews, and grade-distribution data. I wanted the useful context to show up where the decision was happening.</p><h3>What I built</h3><p>A Chrome extension that adds professor ratings and difficulty information alongside course options, with grade-distribution details in a popup. I worked with Clemson’s published grade data, cleaned inconsistent CSVs with Python, and integrated professor ratings through an API.</p><img class="case-image" src="assets/img/optimized/iroar.webp" alt="iRoar Premium displaying professor information and a grade distribution popup in Clemson’s course planner" loading="lazy"><div class="case-links"><a class="text-link" href="https://github.com/Adamruns/iroarpremium" target="_blank" rel="noopener">Explore the repository ↗</a></div><p class="case-note">An independent project, primarily tested in Clemson’s Plan Ahead tool. The illustration on the homepage uses sample bars; this image shows the actual extension.</p>',
  },
  gmc: {
    category: "PERSONAL / COMMUNITY",
    title: "A small build.<br>A reason to exist.",
    body: '<p class="case-lead">An ordering website for GMC Track &amp; Field’s Easter egg fundraiser.</p><h3>Why I built it</h3><p>Useful software does not need a huge brief. A local fundraiser needed a place for people to understand the event and place their orders.</p><h3>The build</h3><p>I used HTML, JavaScript, and agentic AI workflows to bring the site together. It is the kind of project I like: a specific problem, a small surface area, and a reason to get it into people’s hands.</p><div class="case-links"><a class="text-link" href="https://gmceggmyhouse.com" target="_blank" rel="noopener">Visit the project ↗</a></div><p class="case-note">Seasonal fundraiser; ordering availability depends on the event.</p>',
  },
};

function initProjects() {
  const cards = [...document.querySelectorAll(".project-card")];
  const filters = [...document.querySelectorAll("[data-filter]")];
  filters.forEach((button) =>
    button.addEventListener("click", () => {
      filters.forEach((filter) =>
        filter.setAttribute("aria-pressed", String(filter === button)),
      );
      let count = 0;
      cards.forEach((card) => {
        card.hidden =
          button.dataset.filter !== "all" &&
          card.dataset.category !== button.dataset.filter;
        if (!card.hidden) count++;
      });
      document.querySelector("#filter-status").textContent =
        count + " projects shown.";
    }),
  );
  const dialog = document.querySelector("#project-dialog");
  if (!dialog) return;
  const open = setupDialog(dialog);
  document.querySelectorAll("[data-project]").forEach((button) =>
    button.addEventListener("click", () => {
      const project = caseStudies[button.dataset.project];
      if (!project) return;
      // Only trusted, authored case-study copy is inserted here.
      document.querySelector("#project-dialog-content").innerHTML =
        '<p class="eyebrow section-number">' +
        project.category +
        '</p><h2 id="project-dialog-title">' +
        project.title +
        "</h2>" +
        project.body;
      open();
    }),
  );
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

function initClipboard() {
  const button = document.querySelector(".copy-email");
  if (!button) return;
  let timer;
  button.addEventListener("click", async () => {
    const status = document.querySelector("#copy-status");
    clearTimeout(timer);
    try {
      if (!navigator.clipboard) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText("adamruns27@gmail.com");
      status.textContent = "Copied!";
    } catch {
      status.textContent = "Select the email to copy.";
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(document.querySelector(".email-row > a"));
      selection.removeAllRanges();
      selection.addRange(range);
    }
    timer = setTimeout(() => {
      status.textContent = "";
    }, 4000);
  });
}

function initScrollEffects() {
  if (!window.IntersectionObserver || !Element.prototype.animate) return;
  const root = document.documentElement;
  const progress = document.createElement("div");
  progress.className = "reading-progress";
  progress.setAttribute("aria-hidden", "true");
  document.body.appendChild(progress);

  const hero = document.querySelector(".hero");
  const ribbon = document.querySelector(".scroll-ribbon");
  const portrait = document.querySelector(".about-portrait");
  const photos = document.querySelector(".photo-strip");
  const activeAnimations = new Set();
  let scheduled = 0;

  // Animate on entry instead of hiding the page up front: all content stays
  // available without JS, in full-page screenshots, and during keyboard jumps.
  const selectors = [
    ".hero-copy > *",
    ".section-heading > *",
    ".proof-strip > div",
    ".project-card",
    ".about-intro > h2",
    ".about-portrait",
    ".about-content > p",
    ".ai-confession",
    ".experience-list details",
    ".offscreen-interests > div",
    ".photo-button",
    ".contact-heading",
    ".contact-bottom",
    ".gallery-intro > *",
  ];
  const items = [...document.querySelectorAll(selectors.join(","))];
  const observer = new IntersectionObserver(
    (entries) => {
      let sequence = 0;
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        if (
          reducedMotion.matches ||
          entry.target.contains(document.activeElement)
        )
          return;
        const delay = Math.min(sequence++ * 65, 195);
        const animation = entry.target.animate(
          [
            {
              opacity: 0,
              transform: "translateY(32px)",
              filter: "blur(3px)",
            },
            { opacity: 1, transform: "translateY(0)", filter: "blur(0)" },
          ],
          {
            duration: 850,
            delay,
            easing: "cubic-bezier(.16,1,.3,1)",
            fill: "backwards",
          },
        );
        activeAnimations.add(animation);
        animation.finished
          .then(() => activeAnimations.delete(animation))
          .catch(() => activeAnimations.delete(animation));

        if (entry.target.querySelector(".grade-bars")) {
          entry.target
            .querySelectorAll(".grade-bars i")
            .forEach((bar, index) => {
              const grow = bar.animate(
                [{ transform: "scaleY(.04)" }, { transform: "scaleY(1)" }],
                {
                  duration: 1050,
                  delay: delay + index * 85,
                  easing: "cubic-bezier(.22,1,.36,1)",
                  fill: "backwards",
                },
              );
              activeAnimations.add(grow);
              grow.finished
                .then(() => activeAnimations.delete(grow))
                .catch(() => activeAnimations.delete(grow));
            });
        }
      });
    },
    { threshold: 0.08, rootMargin: "0px 0px -35px 0px" },
  );
  items.forEach((item) => observer.observe(item));

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  function update() {
    scheduled = 0;
    const available = root.scrollHeight - innerHeight;
    root.style.setProperty(
      "--reading-progress",
      available > 0 ? clamp(scrollY / available, 0, 1) : 0,
    );
    if (reducedMotion.matches) return;
    const vh = innerHeight;
    if (hero) {
      const bounds = hero.getBoundingClientRect();
      hero.style.setProperty(
        "--hero-drift",
        clamp(-bounds.top * 0.07, -8, 44) + "px",
      );
    }
    if (ribbon) {
      const bounds = ribbon.getBoundingClientRect();
      if (bounds.bottom > -100 && bounds.top < vh + 100) {
        ribbon.style.setProperty(
          "--ribbon-offset",
          -30 -
            (1 - clamp(bounds.top / vh, -0.3, 1)) *
              (innerWidth < 761 ? 140 : 280) +
            "px",
        );
      }
    }
    if (portrait) {
      const bounds = portrait.getBoundingClientRect();
      if (bounds.bottom > 0 && bounds.top < vh)
        portrait.style.setProperty(
          "--portrait-tilt",
          clamp((bounds.top / vh - 0.35) * 5, -1.6, 1.6) + "deg",
        );
    }
    if (photos) {
      const bounds = photos.getBoundingClientRect();
      if (bounds.bottom > 0 && bounds.top < vh)
        photos.style.setProperty(
          "--photo-drift",
          clamp((bounds.top / vh - 0.4) * 25, -10, 10) + "px",
        );
    }
  }
  function schedule() {
    if (!scheduled && !document.hidden)
      scheduled = requestAnimationFrame(update);
  }
  function syncPreference() {
    root.classList.toggle("scroll-effects", !reducedMotion.matches);
    if (reducedMotion.matches)
      activeAnimations.forEach((animation) => animation.cancel());
    schedule();
  }
  // Focus must never land on temporarily transparent content.
  document.addEventListener("focusin", (event) => {
    activeAnimations.forEach((animation) => {
      if (animation.effect?.target?.contains(event.target)) animation.cancel();
    });
  });
  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule, { passive: true });
  document.addEventListener("visibilitychange", schedule);
  window.addEventListener("modalchange", schedule);
  reducedMotion.addEventListener("change", syncPreference);
  new ResizeObserver(schedule).observe(document.body);
  syncPreference();
}

initNavigation();
initProjects();
initPhotos();
initClipboard();
initSculpture();
initScrollEffects();
