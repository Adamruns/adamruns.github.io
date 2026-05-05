# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Personal portfolio site for Adam Smith — vanilla HTML/CSS/JS, no frameworks, no build step. Hosted on GitHub Pages from `master`, served at `adamruns.com` (CNAME).

## Working on the site

- **Preview locally:** open any `.html` file in a browser, or run a static server from the repo root (e.g. `python3 -m http.server 8000`).
- **Deploy:** push to `master`. GitHub Pages picks it up automatically — there is no build, no CI.
- **Cache busting:** `index.html` and the other pages reference `assets/css/style.css?v=2` and `assets/js/main.js?v=2`. Bump the `?v=` query on every page when changing those files, or recently-cached visitors will see stale assets.

## Architecture

### Page structure

Six top-level pages, each a standalone HTML file: `index.html`, `about.html`, `experience.html`, `projects.html`, `photography.html`, `contact.html`. There is no template engine — the `<nav>` block and `<footer>` block are **duplicated verbatim** across all six pages. Any nav/footer change must be applied to every page. The current page's nav link gets `class="active"`.

### CSS

Single stylesheet at `assets/css/style.css`. Theming is driven by CSS custom properties on `:root`, with overrides under `[data-theme="dark"]` — never hardcode colors, use the variables. Spacing also flows through `--space-*` variables. Mobile breakpoint is `max-width: 768px`; an intermediate breakpoint at 769–1024px only adjusts `.photo-grid` columns.

### JavaScript

Single file at `assets/js/main.js`. Four init functions wired up on `DOMContentLoaded`:

- `initNavToggle` — mobile hamburger
- `initScrollAnimations` — IntersectionObserver adds `.visible` to `.fade-in` elements (CSS handles the transition; `.delay-1` … `.delay-5` stagger them)
- `initThemeToggle` — toggles `data-theme` on `<html>`, persists to `localStorage`, falls back to `prefers-color-scheme`
- `initLightbox` — only activates on pages that contain `.photo-grid` (currently only `photography.html`); clicking any `<img>` inside opens it

Each init bails out early if its target elements aren't on the page, so the same script is safe to load everywhere.

### Assets

- `assets/img/photography/` — full-resolution photos shown via the lightbox; HTML uses `loading="lazy"`
- `assets/img/headshot-600.jpg` — used by the hero (a larger `headshot.jpg` original is also kept in the repo)
- `assets/adam_smith_resume.pdf` — linked from the home and experience pages
- `favicon.svg`, `CNAME` — root-level

## Conventions

- Match the existing voice in copy: warm, first-person, conversational. The design doc in `docs/plans/` (gitignored) captures the intent — not boastful, not corporate, not running/brand metaphors.
- Skill/tech tags use the existing `.skill-tag` pill component.
- Keep the stack vanilla. No frameworks, no bundlers, no package.json. The redesign deliberately replaced a jQuery/Bootstrap template — don't reintroduce that complexity.

## Notes

- `docs/` is gitignored; design and planning docs live there locally and aren't deployed.
- `.idea/` is JetBrains config, also gitignored.
