# Repository guidance

Personal portfolio for Adam Smith, hosted by GitHub Pages at `adamruns.com`.
Keep the site vanilla HTML/CSS/JS: no framework, bundler, or application package.json.

## Preview and publish

- Preview with `python3 -m http.server 8765`.
- Adam selected Afterglow and explicitly authorized publishing on October 8, 2026.
- That authorization covers this release; do not require another confirmation for it.
- `master` deploys automatically; preserve `CNAME`.
- CSS and JavaScript references use `?v=7`; bump both pages' references when updating shared assets.

## Architecture

`index.html` is the primary portfolio. `photography.html` contains the full gallery.
`about.html`, `experience.html`, `projects.html`, and `contact.html` redirect old
URLs to homepage anchors and include usable fallback links.
The full pages share header/footer patterns. Keep their navigation and links consistent.

`assets/css/style.css` contains shared layout; `assets/css/afterglow.css` applies the
selected midnight/blue design. Both use custom properties,
self-hosted Manrope and Instrument Serif, and responsive breakpoints at 1050,
760, and 370 pixels. No persistent theme setting is required.

`assets/js/main.js` contains independent initializers. Each checks for its target
before running. Native dialogs provide modal semantics; explicit keyboard cycling
and focus restoration are verified. Preserve reduced-motion behavior, offscreen/
hidden-tab animation suspension, touch scrolling, and meaningful button names.
Project stories are authored static data, not API-fetched or user-provided HTML.

## Content and assets

- Maintain a confident, conversational first-person voice. Use supported achievements,
  not invented metrics or claims of sole ownership when the source describes team work.
- Funding and PR totals are historical snapshots. Funding totals include backfilled
  records, explained in the case study and résumé. Do not imply new revenue generated.
- `assets/adam_smith_resume.tex` is the source for the one-page PDF. Rebuild with
  Tectonic, check page count, extract text, render, and visually inspect changes.
- Preserve original photos; serve optimized WebP derivatives.
- X profile: `https://x.com/tokensmax`; GitHub: `https://github.com/adamruns`;
  LinkedIn: `https://www.linkedin.com/in/adam-robert-smith/`.
- `docs/` is ignored and contains local-only preview tooling and private source notes.
  Never copy raw Career Ops reports, peer statistics, or company records into deployed assets.

## Validation

Check phone widths down to 320px and desktop widths for horizontal overflow.
Verify all filters, six project dialogs, image navigation, clipboard copying,
mobile navigation, legacy URLs, reduced motion, and missing asset requests.
Audit both pages and an open dialog with axe; visually inspect screenshots with
lazy-loaded photos fully loaded before delivery. Keep runtime dependencies at zero. The rejected slingshot game and Matter.js
were removed at Adam's request.

Scroll motion is progressively enhanced with entry animations, a scroll-linked ribbon,
a reading-progress line, and subtle portrait/photo movement. Respect reduced motion
and cancel entry animations when content receives keyboard focus. The supplied Africa
balloon photo replaces the suit portrait on the portfolio. Running is no longer a
featured hobby. Keep Origen anonymous and label the commerce build as awaiting its
first customers; never imply traction or payment-processor integration.

Afterglow is the chosen production design. The original alternatives are archived
locally in ignored `docs/preview/design-options/`. Do not publish the design switcher,
comparison gallery, or rejected game. Theme query parameters no longer change the site.
The `ambient.js` light ribbons run locally without a rendering library or paid API;
`motion.js` contains title reveals and pointer details. Meaningful content is static.

Verify animation pause, hidden/offscreen suspension, reduced motion, contrast, and
widths down to 320px. Keep site navigation consistent across the homepage, gallery,
and Research page. The completed research exports include a reproducibility bundle;
preserve its evidence and keep raw local experiment data out of Git.
