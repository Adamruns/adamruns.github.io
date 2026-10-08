# Adam Smith · adamruns.com

Personal portfolio for Adam Smith, software engineer in Charlotte, NC.
Afterglow is the selected design: midnight blue, flowing light ribbons, subtle
scroll reveals, and responsive layouts. Vanilla HTML, CSS, and JavaScript;
no build step, third-party renderer, or paid API.

## Local preview

```sh
python3 -m http.server 8765
```

Open http://localhost:8765. For a phone on the same Wi-Fi, use the computer's
local IP and port 8765. The previous design alternatives are archived locally
under ignored `docs/preview/design-options/` and are not published.

## Structure

- `index.html`: career highlights, animated hero, filterable work, experience,
  selected photographs, and contact links.
- `photography.html`: full collection with keyboard/touch image navigation.
- `unit-testing.html`: completed AI testing pilot, measured results, chart,
  public evidence bundle, and methodology. Runner documentation is in
  `experiments/unit-testing/README.md`; private local runs stay in ignored `docs/preview/`.
- `about.html`, `experience.html`, `projects.html`, `contact.html`: preserve old
  URLs and redirect to the relevant homepage sections.
- `assets/css/style.css`: shared layout and components.
- `assets/css/afterglow.css`: the selected palette, hero, responsive overrides,
  and pointer effects.
- `assets/js/main.js`: filters, dialogs, navigation, photo viewer, clipboard,
  and scroll motion.
- `assets/js/ambient.js`: the original light-ribbon canvas, shape controls,
  pause, and offscreen/hidden-tab suspension.
- `assets/js/motion.js`: title reveals and gentle pointer responses.
- `assets/adam_smith_resume.pdf`: current one-page website résumé.
- `assets/adam_smith_resume.tex`: editable source. Rebuild with
  `tectonic assets/adam_smith_resume.tex --outdir assets` and inspect the output.
- `assets/fonts`: self-hosted WOFF2 files and their OFL licenses.
- `assets/img/optimized`: resized, EXIF-oriented WebP derivatives; original
  photographs remain in `assets/img/photography`.

Animations respect reduced motion and pause behind dialogs or when hidden.
The canvas caps pixel density at 2 and renders at approximately 30 fps, with
fewer paths on narrow screens. Historical career figures are explicitly dated.

## Publishing

Adam approved Afterglow and publication on October 8, 2026. GitHub Pages serves
`master` at `adamruns.com` via `CNAME`; pushing that branch deploys automatically.
`.nojekyll` keeps this a static site. Shared assets currently use `?v=7` for cache
invalidation. Verify Pages build completion and the actual custom-domain HTML
and assets after publishing.

Local screenshots, source notes, design alternatives, and validation reports
live in ignored `docs/preview/`. They must not enter the public commit.
