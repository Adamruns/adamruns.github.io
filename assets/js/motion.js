(() => {
  const root = document.documentElement;
  const motion = matchMedia("(prefers-reduced-motion: reduce)");
  const fine = matchMedia("(hover:hover) and (pointer:fine)");
  const title = document.querySelector(".hero h1");
  if (title) {
    const lines = title.innerHTML.split(/<br\s*\/?\s*>/i);
    title.innerHTML = lines
      .map((line) => `<span class="title-line"><span>${line}</span></span>`)
      .join("");
    if (!motion.matches)
      title.querySelectorAll(".title-line > span").forEach((line, i) => {
        const anim = line.animate(
          [
            { transform: "translateY(110%) rotate(3deg)" },
            { transform: "translateY(0) rotate(0)" },
          ],
          {
            duration: 1100,
            delay: 120 + i * 110,
            easing: "cubic-bezier(.16,1,.3,1)",
            fill: "backwards",
          },
        );
        motion.addEventListener(
          "change",
          () => {
            if (motion.matches) anim.cancel();
          },
          { once: true },
        );
      });
  }
  function sync() {
    root.classList.toggle("motion-enabled", !motion.matches && fine.matches);
    if (motion.matches) {
      document
        .querySelectorAll(".hero-actions .button,.header-contact")
        .forEach((button) => button.style.removeProperty("translate"));
      document.querySelectorAll(".project-card").forEach((c) => {
        c.style.removeProperty("--tilt-x");
        c.style.removeProperty("--tilt-y");
      });
    }
  }
  document.querySelectorAll(".project-card").forEach((card) => {
    let frame = 0,
      position = null;
    card.addEventListener(
      "pointermove",
      (event) => {
        if (motion.matches || !fine.matches || event.pointerType === "touch")
          return;
        position = { x: event.clientX, y: event.clientY };
        if (frame) return;
        frame = requestAnimationFrame(() => {
          frame = 0;
          const r = card.getBoundingClientRect(),
            x = position.x - r.left,
            y = position.y - r.top;
          card.style.setProperty("--light-x", x + "px");
          card.style.setProperty("--light-y", y + "px");
          card.style.setProperty(
            "--tilt-x",
            (0.5 - y / r.height) * 2.1 + "deg",
          );
          card.style.setProperty("--tilt-y", (x / r.width - 0.5) * 2.1 + "deg");
        });
      },
      { passive: true },
    );
    card.addEventListener("pointerleave", () => {
      if (frame) {
        cancelAnimationFrame(frame);
        frame = 0;
      }
      card.style.setProperty("--tilt-x", "0deg");
      card.style.setProperty("--tilt-y", "0deg");
    });
  });
  document
    .querySelectorAll(".hero-actions .button,.header-contact")
    .forEach((button) => {
      button.addEventListener(
        "pointermove",
        (event) => {
          if (motion.matches || !fine.matches) return;
          const r = button.getBoundingClientRect();
          button.style.translate = `${(event.clientX - r.left - r.width / 2) * 0.07}px ${(event.clientY - r.top - r.height / 2) * 0.1}px`;
        },
        { passive: true },
      );
      button.addEventListener("pointerleave", () =>
        button.style.removeProperty("translate"),
      );
    });
  motion.addEventListener("change", sync);
  fine.addEventListener("change", sync);
  sync();
})();
