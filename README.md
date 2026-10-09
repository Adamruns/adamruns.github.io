# Adam Smith · adamruns.com

Adam's résumé site: experience, education, skills, projects, research, and photos.
Midnight-blue Afterglow palette with one automatically animated light ribbon.
Vanilla HTML, CSS, and JavaScript; no build step or paid API.

## Local preview

```sh
python3 -m http.server 8765
```

Open http://localhost:8765. Local QA tooling, recordings, and previous design
alternatives are in ignored `docs/preview/`; they are not published.

## Structure

- `index.html`: résumé homepage with a hero, Experience (including a July 2026
  figures ledger), Education, Skills, Projects, Research, Outside work, and Contact.
- `photography.html`: full gallery with keyboard and touch image navigation.
- `unit-testing.html`, `user-confidence.html`: completed AI experiments with results,
  evidence, and methodology. See `experiments/*/README.md` for the runners. Private
  runs stay in `docs/`.
- `about.html`, `experience.html`, `projects.html`, `contact.html`: legacy redirects.
- `assets/css/style.css`: shared tokens, header, footer, gallery, dialog, and research
  page base styles.
- `assets/css/afterglow.css`: homepage-only résumé layout.
- `assets/js/main.js`: photo dialogs and the mobile menu.
- `assets/js/ambient.js`: automatically animated ribbon canvas in the hero.
- `assets/img/projects`: actual project screenshots. The iRoar image uses the local
  extension UI with sample data, explicitly labeled; no student records were used.
- `assets/adam_smith_resume.pdf`: one-page résumé; source is the matching `.tex` file.
- `assets/fonts`: self-hosted WOFF2 files and their OFL licenses.
- `assets/img/optimized`: WebP photos. Original photographs are preserved.

The hero has one entrance sequence and an animated ribbon that pauses offscreen,
behind a photo dialog, and when the tab is hidden. Reduced-motion preferences show
static visuals.

## Publishing and checks

GitHub Pages serves `master` at `adamruns.com` via `CNAME`; pushes deploy
automatically. Shared assets use `?v=10`.

Inspect 320px, 390px, tablet, and desktop layouts, the mobile menu, keyboard
navigation, photo dialogs, ribbon motion and suspension, reduced motion, research
pages, and legacy redirects. Check axe and missing assets. After pushing, verify the
Pages build and the actual custom-domain HTML and assets.

Keep raw captures, sample fixtures, local screenshots, and private source notes
in ignored `docs/`. Never publish Career Ops reports or company records.
