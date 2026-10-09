# Repository guidance

Personal résumé site for Adam Smith, hosted by GitHub Pages at `adamruns.com`.
Keep the site vanilla HTML/CSS/JS: no framework, bundler, or application package.json.

## Preview and publish

- Preview with `python3 -m http.server 8765`.
- Adam selected the Afterglow palette on October 8, 2026, and on October 9, 2026
  asked for a résumé-focused rewrite aimed at employers and its deployment.
- `master` deploys automatically; preserve `CNAME`.
- CSS and JavaScript references use `?v=10`; bump every page's references when
  updating shared assets (including the template in `experiments/user-confidence/page.py`).

## Architecture

`index.html` is the résumé homepage: hero, Experience, Education, Skills, Projects,
Research, Outside work, and Contact. `photography.html` contains the full gallery.
`about.html`, `experience.html`, `projects.html`, and `contact.html` redirect old
URLs to homepage anchors and include usable fallback links.
Every full page shares the same `site-header` (wordmark, nav, Résumé button, mobile
Menu button) and `site-footer`. Keep their navigation and links consistent.

`assets/css/style.css` is shared by every page: tokens, fonts, header, footer,
buttons, gallery, photo dialog, and the base classes the research pages use.
`assets/css/afterglow.css` is homepage-only. Both use custom properties,
self-hosted Manrope and Instrument Serif (italic, for h1/h2), and responsive
breakpoints at 1050, 760, and 370 pixels. No persistent theme setting is required.

`assets/js/main.js` contains independent initializers (photo dialog, mobile menu).
Each checks for its target before running. Pages add a `js` class to `<html>` inline
so the mobile menu only collapses when scripting works. Native dialogs provide modal
semantics; explicit keyboard cycling and focus restoration are verified.

## Content and assets

- Maintain a confident, conversational first-person voice. Use supported achievements,
  not invented metrics or claims of sole ownership when the source describes team work.
- `assets/adam_smith_resume.tex` is the source of truth for experience copy. Site
  figures must match it. Funding and PR totals are July 2026 snapshots; funding totals
  include backfilled records, as the homepage ledger note says. Do not imply revenue.
- Rebuild the PDF with Tectonic, check page count, extract text, render, and visually
  inspect changes.
- Preserve original photos; serve optimized WebP derivatives.
- X profile: `https://x.com/tokensmax`; GitHub: `https://github.com/adamruns`;
  LinkedIn: `https://www.linkedin.com/in/adam-robert-smith/`.
- `docs/` is ignored and contains local-only preview tooling and private source notes.
  Never copy raw Career Ops reports, peer statistics or rankings, performance-review
  quotes, internal dollar figures, or company records into deployed assets.

## Motion

Motion is limited to one hero entrance sequence and the `ambient.js` light ribbon,
which runs locally without a rendering library or paid API. The ribbon pauses
offscreen, behind a photo dialog, and in hidden tabs. Reduced motion shows static
visuals. Do not add per-section scroll reveals. Meaningful content is static.

## Validation

Check phone widths down to 320px and desktop widths for horizontal overflow.
Verify the mobile menu (open, link close, Escape with focus return), photo dialogs
(arrows, swipe, focus trapping and restoration), legacy URLs, reduced motion, ribbon
suspension, and missing asset requests. Audit the homepage, gallery, research pages,
and an open dialog with axe; visually inspect screenshots with lazy-loaded photos
fully loaded before delivery. Keep runtime dependencies at zero.

The completed research exports include a reproducibility bundle; preserve its
evidence and keep raw local experiment data out of Git. Keep Origen anonymous if it
is ever featured, label the commerce build as awaiting its first customers, and never
imply traction or payment-processor integration.
