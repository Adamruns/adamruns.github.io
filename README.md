# Adam Smith · adamruns.com

Adam's personal page: a short intro, projects, research, and photos.
Afterglow uses midnight blue and automatically animated light ribbons.
Vanilla HTML, CSS, and JavaScript; no build step or paid API.

## Local preview

```sh
python3 -m http.server 8765
```

Open http://localhost:8765. Local QA tooling, recordings, and previous design
alternatives are in ignored `docs/preview/`; they are not published.

## Structure

- `index.html`: personal intro, two project previews, research link, and three photos.
- `photography.html`: full gallery with keyboard and touch image navigation.
- `unit-testing.html`: completed AI testing pilot, results, evidence, and methodology.
  See `experiments/unit-testing/README.md` for the runner. Private runs stay in `docs/`.
- `about.html`, `experience.html`, `projects.html`, `contact.html`: legacy redirects.
- `assets/css/style.css`: shared base styles, gallery, and dialog components.
- `assets/css/afterglow.css`: selected palette and personal-page layout.
- `assets/js/main.js`: photo dialogs, gentle project-preview motion, and scroll reveals.
- `assets/js/ambient.js`: automatically animated ribbon canvas. No hero controls.
- `assets/img/projects`: actual project screenshots. The iRoar image uses the local
  extension UI with sample data, explicitly labeled; no student records were used.
- `assets/adam_smith_resume.pdf`: one-page résumé; source is the matching `.tex` file.
- `assets/fonts`: self-hosted WOFF2 files and their OFL licenses.
- `assets/img/optimized`: WebP photos. Original photographs are preserved.

The hero animates continuously while visible. Project screenshots have a slow
pan and zoom. Both pause offscreen, behind a photo dialog, and when the tab is
hidden. Reduced-motion preferences show static visuals. There are no video
players, motion-control buttons, banner slogans, or portrait captions.

## Publishing and checks

Adam approved Afterglow and publication, then requested a shorter personal page
with automatic animation. GitHub Pages serves `master` at `adamruns.com` via
`CNAME`; pushes deploy automatically. Shared assets use `?v=9`.

Inspect desktop and 320px/390px layouts, keyboard navigation, photo dialogs,
continuous motion, offscreen suspension, reduced motion, research loading, and
legacy redirects. Check axe and missing assets. After pushing, verify the Pages
build and the actual custom-domain HTML and assets.

Keep raw captures, sample fixtures, local screenshots, and private source notes
in ignored `docs/`. Never publish Career Ops reports or company records.
