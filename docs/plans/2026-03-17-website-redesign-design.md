# Website Redesign: adamruns.com

## Overview

Complete redesign of adamruns.github.io as a personal portfolio site linked to adamruns.com (domain on Cloudflare). Replaces the outdated jQuery/Bootstrap template with a clean, modern, multi-page static site.

## Goals

- Present Adam as a Software Engineer II at MedShift, not a college student
- Warm, personal, approachable aesthetic that stands out from dark-mode developer sites
- Easy to maintain and update (vanilla HTML/CSS/JS, no build step)
- Future-proof for adding a photography page

## Tech Stack

- Vanilla HTML5, CSS3, JavaScript
- No frameworks, no build tools
- GitHub Pages hosting
- Custom domain: adamruns.com via Cloudflare

## Design Direction

- **Palette:** Off-white backgrounds, charcoal text, one warm accent color (terracotta/amber/sage range — complements the blue shirt + warm tones in headshot)
- **Typography:** Clean sans-serif (Inter or DM Sans) for body, optionally a more distinctive font for headings
- **Vibe:** Warm and personal. First-person copy, conversational tone, confident but not boastful.

## Site Structure

### Navigation

Persistent top nav bar across all pages:

```
[Adam Smith]                    [About]  [Experience]  [Projects]  [Contact]
```

- Name/logo on left links home
- Nav links right-aligned
- Mobile: hamburger menu
- Active page highlighted

### Footer

Shared across all pages: GitHub + LinkedIn icons, copyright line.

### Pages

#### 1. Home (`index.html`)

Hero section — everything above the fold, no scrolling needed.

- Headshot on left (circular or soft-rounded), text on right
- Name (large, confident), title ("Software Engineer II at MedShift"), location ("Charlotte, NC")
- 1-2 sentence intro — genuine, not corporate. Captures: full-stack work, building with AI.
- CTA buttons: View Resume (PDF download), GitHub, LinkedIn
- Stacks vertically on mobile

#### 2. About (`about.html`)

Three sections with subtle dividers:

1. **Story** — 2-3 paragraphs: background, what you do now (MedShift, agentic AI), M.S. at Clemson while working full-time
2. **What I Work With** — tech skills as clean pill/tag elements (no progress bars): Python, TypeScript, Django, Vue.js, PostgreSQL, Docker, AWS, Redis, etc.
3. **Outside of Code** — 1-2 sentences about running, guitar, photography, sports

#### 3. Experience (`experience.html`)

Resume in web form, more scannable than a PDF.

- Vertical stacking with dates right-aligned (dates stack below on mobile)
- Company name + title prominent, bullet points underneath
- MedShift: both roles (SWE II and SWE I) grouped under one company header
- Roles in order: MedShift, Prisma Health, ScopeStack, Fortis, BoltAffect
- Education section below: M.S. CS (expected May 2026, 4.0 GPA, AI/ML focus), B.S. CS (Dec 2024, Palmetto Fellows)
- "Download Resume PDF" button at bottom

#### 4. Projects (`projects.html`)

Curated showcase — quality over quantity.

- 2-column card grid (single column on mobile)
- Each card: screenshot/visual, title, 1-2 sentence description, tech pills, link (GitHub or live site)
- No filtering — curated list of 4-6 best projects
- Subtle hover effect (lift or shadow)
- Exact projects TBD during implementation

#### 5. Contact (`contact.html`)

Minimal.

- Short friendly line ("Want to connect? Feel free to reach out.")
- Email as clickable mailto: link (adamruns27@gmail.com)
- GitHub + LinkedIn icon links
- No contact form

## Not Doing

- No JS frameworks or build tools
- No skill percentage/progress bars
- No isotope filtering on projects
- No contact form
- No running/brand metaphors — "adamruns" is just the handle
- No blog (for now)

## Future Additions

- Photography page — structure supports adding as another nav item + page
