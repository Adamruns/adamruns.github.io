/* Afterglow: an original responsive light study, drawn locally at 30 fps. */
function initSculpture() {
  const canvas = document.querySelector("#system-canvas");
  const ctx = canvas?.getContext("2d");
  if (!ctx) return;
  const stage = canvas.closest(".system-playground");
  const hero = stage.closest(".hero");
  const pause = stage.querySelector(".motion-toggle");
  const motion = matchMedia("(prefers-reduced-motion: reduce)");
  const tau = Math.PI * 2;
  let width = 0,
    height = 0,
    frame = 0,
    last = 0,
    clock = 0,
    shape = 0;
  let visible = true,
    paused = motion.matches,
    scroll = 0,
    x = 0.15,
    y = -0.15,
    targetX = 0.15,
    targetY = -0.15;
  let breadth = 1.3,
    frequency = 2;
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  function draw() {
    if (!width || !height) return;
    ctx.clearRect(0, 0, width, height);
    const scale = Math.min(width * 0.36, height * 0.43),
      cx = width * 0.53,
      cy = height * 0.51;
    const rotation = -0.55 + x * 0.18 + scroll * 0.12;
    const rows = width < 500 ? 32 : 42,
      columns = width < 500 ? 76 : 94;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(rotation);
    const gradient = ctx.createLinearGradient(-scale, -scale, scale, scale);
    gradient.addColorStop(0, "#535ee0");
    gradient.addColorStop(0.4, "#80c9ff");
    gradient.addColorStop(0.68, "#bfafff");
    gradient.addColorStop(1, "#255cf1");
    for (let row = 0; row < rows; row++) {
      const v = row / (rows - 1),
        phase = v * tau;
      ctx.strokeStyle = gradient;
      ctx.globalAlpha = 0.22 + 0.56 * Math.sin(v * Math.PI);
      ctx.lineWidth = width < 500 ? 0.8 : 1.2;
      ctx.beginPath();
      for (let i = 0; i <= columns; i++) {
        const u = (i / columns) * tau;
        const wave = Math.sin(u * frequency + clock * 0.45 + phase) * 0.14;
        const r = 0.7 + 0.22 * Math.cos(phase) + wave;
        const px = Math.cos(u) * r * scale * breadth;
        const py =
          Math.sin(u) * scale * (0.62 + 0.32 * Math.sin(phase)) +
          Math.sin(u * 2 + clock * 0.35) * scale * 0.16 +
          y * scale * 0.2;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      if (row % 8 === 0) {
        ctx.shadowBlur = 12;
        ctx.shadowColor = "#719aff";
      } else ctx.shadowBlur = 0;
      ctx.stroke();
    }
    ctx.restore();
    ctx.shadowBlur = 0;
    ctx.globalAlpha = 1;
  }
  function allowed() {
    return (
      visible &&
      !paused &&
      !document.hidden &&
      !document.body.classList.contains("modal-open")
    );
  }
  function tick(now) {
    frame = 0;
    if (!allowed()) return;
    if (now - last > 30) {
      const dt = Math.min(now - last, 65);
      clock += dt / 1000;
      x += (targetX - x) * 0.09;
      y += (targetY - y) * 0.09;
      breadth += ((shape === 1 ? 0.85 : 1.3) - breadth) * 0.09;
      frequency += ((shape === 2 ? 3 : 2) - frequency) * 0.09;
      draw();
      last = now;
    }
    frame = requestAnimationFrame(tick);
  }
  function sync() {
    if (allowed() && !frame) {
      last = performance.now();
      frame = requestAnimationFrame(tick);
    } else if (!allowed() && frame) {
      cancelAnimationFrame(frame);
      frame = 0;
    }
  }
  function updatePause() {
    pause.setAttribute("aria-pressed", String(paused));
    pause.setAttribute(
      "aria-label",
      paused ? "Play sculpture animation" : "Pause sculpture animation",
    );
    pause.firstElementChild.textContent = paused ? "▷" : "Ⅱ";
    sync();
  }
  function resize() {
    width = canvas.clientWidth;
    height = canvas.clientHeight;
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw();
  }
  hero.addEventListener(
    "pointermove",
    (event) => {
      if (event.pointerType === "touch" || motion.matches) return;
      const rect = hero.getBoundingClientRect();
      targetX = (event.clientX - rect.left) / rect.width - 0.5;
      targetY = (event.clientY - rect.top) / rect.height - 0.5;
    },
    { passive: true },
  );
  hero.addEventListener("pointerleave", () => {
    targetX = 0.15;
    targetY = -0.15;
  });
  window.addEventListener(
    "scroll",
    () => {
      if (!motion.matches)
        scroll = clamp(-stage.getBoundingClientRect().top / innerHeight, -1, 1);
    },
    { passive: true },
  );
  stage.querySelectorAll("[data-shape]").forEach((button) =>
    button.addEventListener("click", () => {
      shape = Number(button.dataset.shape);
      if (paused) {
        breadth = shape === 1 ? 0.85 : 1.3;
        frequency = shape === 2 ? 3 : 2;
      }
      stage
        .querySelectorAll("[data-shape]")
        .forEach((node) =>
          node.setAttribute("aria-pressed", String(node === button)),
        );
      stage.querySelector("#orbit-label").textContent = [
        "IDEA → SYSTEM",
        "CONTEXT → CONNECTION",
        "CURIOSITY → POSSIBILITY",
      ][shape];
      draw();
      sync();
    }),
  );
  pause.addEventListener("click", () => {
    paused = !paused;
    updatePause();
  });
  motion.addEventListener("change", () => {
    paused = motion.matches;
    updatePause();
    draw();
  });
  new ResizeObserver(resize).observe(canvas);
  new IntersectionObserver(
    (entries) => {
      visible = entries[0].isIntersecting;
      sync();
    },
    { threshold: 0.05 },
  ).observe(stage);
  document.addEventListener("visibilitychange", sync);
  window.addEventListener("modalchange", sync);
  stage.classList.add("canvas-ready");
  resize();
  updatePause();
}
