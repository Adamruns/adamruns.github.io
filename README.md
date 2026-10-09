# Adam Smith · adamruns.com

Adam's personal page: a short intro, project demos, research, and photos.
The selected Afterglow design uses midnight blue and a light-ribbon canvas.
Vanilla HTML, CSS, and JavaScript; no build step or paid API.

## Local preview

```sh
python3 -m http.server 8765
```

Open http://localhost:8765. The previous design alternatives and local QA tools
are in ignored `docs/preview/`; they are not published.

## Structure

- `index.html`: personal intro, two project videos, research link, and three photos.
- `photography.html`: full gallery with keyboard and touch image navigation.
- `unit-testing.html`: completed AI testing pilot, results, evidence, and methodology.
  Runner documentation is in `experiments/unit-testing/README.md`; private experiment
  runs stay in ignored `docs/preview/`.
- `about.html`, `experience.html`, `projects.html`, `contact.html`: legacy redirects
  to homepage anchors.
- `assets/css/style.css`: shared base styles, gallery, and dialog components.
- `assets/css/afterglow.css`: the selected palette and personal-page layout.
- `assets/js/main.js`: photo dialogs, video playback coordination, and entry reveals.
- `assets/js/ambient.js`: a four-second ribbon entrance, followed by scroll response.
  There is no idle animation loop or hero control panel.
- `assets/video`: two silent H.264 MP4 demos, with optional English captions.
- `assets/img/demos`: optimized video posters.
- `assets/adam_smith_resume.pdf`: one-page résumé; editable source is the matching
  `.tex` file. Rebuild with Tectonic and visually verify any résumé edits.
- `assets/fonts`: self-hosted WOFF2 files and their OFL licenses.
- `assets/img/optimized`: WebP photos. Original photographs are preserved.

## Demo provenance

Smith & Shin is a recording of the actual public website: homepage, Services,
and Tax Tips. No forms were submitted.

iRoar Premium is the actual local extension UI (`registration.js` and
`registration.css`, version 2.0) with mocked course, professor, rating, and grade
responses. The recording is visibly labeled as a local demo with sample data.
It demonstrates searching, opening course details, and comparing semesters.
It does not establish live Clemson integration or a successful registration.
No student records or real login session were used.

Both videos require a user gesture and use `preload="none"`. Only one plays at
a time; playback pauses when offscreen, the page is hidden, or a photo opens.
Reduced-motion preferences disable entry and scroll animation. All meaningful
content, navigation, videos, and photographs work without JavaScript; the photo
lightbox is progressive enhancement.

## Publishing and checks

Adam approved Afterglow and publication on October 8, 2026, then requested a
shorter personal page with demos and no slogans or hero controls. GitHub Pages
serves `master` at `adamruns.com` via `CNAME`; pushes deploy automatically.
Shared assets use `?v=8` for cache invalidation.

Before publishing, inspect desktop and 320px/390px layouts, video playback and
captions, keyboard navigation, photo dialogs, reduced motion, research loading,
and legacy redirects. Check axe, missing assets, and that videos are not fetched
before playback. After pushing, verify the Pages build and custom-domain assets.

Keep raw captures, sample fixtures, local screenshots, and private source notes
in ignored `docs/`. Never publish Career Ops reports or company records.
