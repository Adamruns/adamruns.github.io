/* Afterglow light ribbons. Autoplays while visible; no control panel. */
function initAfterglow() {
  const canvas = document.querySelector("#afterglow-canvas");
  const ctx = canvas?.getContext("2d");
  if (!ctx || !window.ResizeObserver || !window.IntersectionObserver) return;
  const intro = canvas.closest(".intro");
  const motion = matchMedia("(prefers-reduced-motion: reduce)");
  const tau = Math.PI * 2;
  let width = 0,
    height = 0,
    frame = 0,
    last = 0,
    elapsed = 0;
  let visible = true,
    scroll = 0,
    clock = 0;
  const x = 0.15,
    y = -0.15,
    breadth = 1.3,
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
      !document.hidden &&
      !document.body.classList.contains("modal-open")
    );
  }
  function tick(now) {
    frame = 0;
    if (!allowed()) return;
    if (motion.matches) {
      clock = 0;
      draw();
      return;
    }
    if (now - last >= 32) {
      elapsed += Math.min(now - last, 65) / 1000;
      clock = elapsed + scroll * 1.2;
      draw();
      last = now;
    }
    frame = requestAnimationFrame(tick);
  }
  function sync() {
    if (frame) cancelAnimationFrame(frame);
    frame = 0;
    if (!allowed()) return;
    if (motion.matches) {
      clock = 0;
      draw();
    } else {
      last = performance.now();
      frame = requestAnimationFrame(tick);
    }
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
  let scrollFrame = 0;
  window.addEventListener(
    "scroll",
    () => {
      if (motion.matches || !allowed() || scrollFrame) return;
      scrollFrame = requestAnimationFrame(() => {
        scrollFrame = 0;
        scroll = clamp(-intro.getBoundingClientRect().top / innerHeight, -1, 1);
      });
    },
    { passive: true },
  );
  motion.addEventListener("change", () => {
    sync();
  });
  new ResizeObserver(resize).observe(canvas);
  new IntersectionObserver((entries) => {
    visible = entries[0].isIntersecting;
    sync();
  }).observe(intro);
  document.addEventListener("visibilitychange", sync);
  window.addEventListener("modalchange", sync);
  resize();
  sync();
}
