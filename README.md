# Adam Smith · adamruns.com

Adam's résumé site: experience, GitHub activity, education, skills, projects, and photos.
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
  figures ledger), On GitHub, Education, Skills, Projects, Outside work, and Contact.
- `photography.html`: full gallery with keyboard and touch image navigation.
- `about.html`, `experience.html`, `projects.html`, `contact.html`: legacy redirects.
- `assets/css/style.css`: shared tokens, header, footer, gallery, and dialog styles.
- `assets/css/afterglow.css`: homepage-only résumé layout.
- `assets/js/main.js`: photo dialogs, the mobile menu, and the activity calendar.
- `assets/data/github-activity.json`: daily contribution counts, refreshed by
  `scripts/update_github_activity.py` through `.github/workflows/github-activity.yml`.
  Requires "Include private contributions on my profile" on Adam's GitHub account.
- `assets/js/ambient.js`: automatically animated ribbon canvas in the hero.
- `assets/img/projects`: real project screenshots. Samba screens come from its Expo
  web build; Egg My House was captured in its open-orders state.
- `assets/adam_smith_resume.pdf`: one-page résumé; source is the matching `.tex` file.
- `assets/fonts`: self-hosted WOFF2 files and their OFL licenses.
- `assets/img/optimized`: WebP photos. Original photographs are preserved.

The hero has one entrance sequence and an animated ribbon that pauses offscreen,
behind a photo dialog, and when the tab is hidden. Reduced-motion preferences show
static visuals.

## Publishing and checks

GitHub Pages serves `master` at `adamruns.com` via `CNAME`; pushes deploy
automatically. Shared assets use `?v=11`.

Inspect 320px, 390px, tablet, and desktop layouts, the mobile menu, keyboard
navigation, photo dialogs, the activity calendar, ribbon motion and suspension,
reduced motion, and legacy redirects. Check axe and missing assets. After pushing, verify the
Pages build and the actual custom-domain HTML and assets.

Keep raw captures, sample fixtures, local screenshots, and private source notes
in ignored `docs/`. Never publish Career Ops reports or company records.
