# Website Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete redesign of adamruns.github.io as a warm, personal, multi-page portfolio at adamruns.com.

**Architecture:** Multi-page static site with shared nav/footer, vanilla HTML/CSS/JS. No frameworks, no build tools. CSS custom properties for theming. Mobile-first responsive design.

**Tech Stack:** HTML5, CSS3, vanilla JavaScript. Google Fonts (Inter + DM Sans). GitHub Pages + Cloudflare DNS.

**Design doc:** `docs/plans/2026-03-17-website-redesign-design.md`

**Style guides:** `~/.claude/style-guides/general/conventions.md`, `~/.claude/style-guides/languages/html-css.md`, `~/.claude/style-guides/languages/javascript.md`

---

### Task 1: Copy Assets and Set Up New Directory Structure

**Goal:** Bring in the new headshot, resume, and favicon. Create the new file structure alongside the old files (we'll clean up old files at the end).

**Step 1: Copy headshot and resume into assets**

```bash
cp "/Users/adamsmith/Documents/Headshots/linkedin.jpg" "/Users/adamsmith/Desktop/Projects/Personal/adamruns.github.io/assets/img/headshot.jpg"
cp "/Users/adamsmith/Documents/Resumes/Resume (1).pdf" "/Users/adamsmith/Desktop/Projects/Personal/adamruns.github.io/assets/adam_smith_resume.pdf"
```

**Step 2: Create an optimized version of the headshot**

Use `sips` (macOS built-in) to create a smaller web-optimized version:

```bash
sips -Z 600 --setProperty formatOptions 80 "/Users/adamsmith/Desktop/Projects/Personal/adamruns.github.io/assets/img/headshot.jpg" --out "/Users/adamsmith/Desktop/Projects/Personal/adamruns.github.io/assets/img/headshot-600.jpg"
```

**Step 3: Commit**

```bash
git add assets/img/headshot.jpg assets/img/headshot-600.jpg assets/adam_smith_resume.pdf
git commit -m "Add new headshot and updated resume"
```

---

### Task 2: CSS Design System (`assets/css/style.css`)

**Goal:** Create the full CSS file with design tokens, reset, typography, layout utilities, nav, footer, and all component styles. This is the largest task — the entire visual language of the site.

**Files:**
- Create: `assets/css/style.css`

**Design tokens:**

```
Colors:
  --color-bg:          #faf8f5    (warm off-white)
  --color-bg-card:     #f3ede7    (slightly warmer for cards)
  --color-text:        #2d2d2d    (soft charcoal)
  --color-text-muted:  #6b6560    (muted for secondary text)
  --color-accent:      #c4704b    (terracotta — complements blue shirt + warm skin)
  --color-accent-hover:#a85d3c    (darker terracotta)
  --color-border:      #e0d8d0    (warm gray border)
  --color-white:       #ffffff

Typography:
  --font-heading: 'DM Sans', sans-serif
  --font-body:    'Inter', sans-serif

Spacing:
  --space-xs: 0.25rem
  --space-sm: 0.5rem
  --space-md: 1rem
  --space-lg: 2rem
  --space-xl: 3rem
  --space-2xl: 5rem

Layout:
  --max-width: 1100px
  --nav-height: 72px
```

**Step 1: Write `assets/css/style.css`**

The CSS file should include, in order:

1. **CSS custom properties** (`:root` block with all tokens above)
2. **Reset** — minimal: `*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }`, sensible defaults for body, headings, links, images, lists
3. **Typography** — base body styles (font-family, size, line-height, color), heading scales (h1 through h4 using `--font-heading`), paragraph margin, link styles (accent color, underline on hover)
4. **Layout utilities** — `.container` (max-width + auto margins + padding), `.section` (padding-top/bottom for page sections)
5. **Navigation** — fixed top bar, 72px height, white background, subtle bottom border. Logo/name left (bold, charcoal, links home). Nav links right, horizontal, 1rem gap. Active link gets accent color + bottom border. Mobile: hamburger button (hidden on desktop), slide-in overlay menu.
6. **Footer** — centered, subtle top border, padding, muted text, social icon links
7. **Buttons** — `.button-primary` (accent bg, white text, rounded, padding), `.button-outline` (border only, accent text). Hover states for both. `.button-icon` for social icon links.
8. **Hero section** (home page) — flexbox, two columns (image left, text right), vertically centered, full viewport height minus nav. Headshot: 280px, circular (`border-radius: 50%`), subtle box-shadow. On mobile: stack vertically, image on top, smaller (200px).
9. **About page** — `.about-story` (max-width: 720px for readable line length), `.skill-tags` (flex wrap container), `.skill-tag` (pill style: rounded, padding, bg-card background, small text), `.about-interests` (muted text)
10. **Experience page** — `.timeline` container. `.timeline-entry` with left border (accent color, 2px). Company name + date on same line (flexbox, space-between). Role title styled distinctly. Bullet points with normal list styling. `.education-entry` similar but simpler. Mobile: dates stack below company name.
11. **Projects page** — `.project-grid` (CSS grid, 2 columns, gap). `.project-card` (bg-card background, rounded corners, overflow hidden). Card image at top (aspect-ratio: 16/9, object-fit: cover). Card body with padding, title, description, tech tags. Hover: subtle translateY(-4px) + shadow. Mobile: single column.
12. **Contact page** — centered text, email link styled large, social links row
13. **Responsive** — `@media (max-width: 768px)` for all mobile overrides: nav hamburger, hero stacking, timeline date stacking, project grid single column, general spacing reductions

**Step 2: Verify CSS parses correctly**

Open any of the HTML files (once created) in browser and check dev tools for CSS parse errors.

**Step 3: Commit**

```bash
git add assets/css/style.css
git commit -m "Add CSS design system with all component styles"
```

---

### Task 3: Home Page (`index.html`)

**Goal:** Build the landing page — hero with headshot, name, title, intro, and links.

**Files:**
- Create: `index.html` (this will overwrite the existing one — that's intentional, this is a full redesign)

**Step 1: Write `index.html`**

Structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Adam Smith — Software Engineer II at MedShift. Building full-stack applications with Vue, Django, and Python.">
  <title>Adam Smith — Software Engineer</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@500;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
  <nav class="nav">
    <div class="nav-container">
      <a href="index.html" class="nav-logo">Adam Smith</a>
      <button class="nav-toggle" aria-label="Toggle navigation">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav-links">
        <li><a href="about.html">About</a></li>
        <li><a href="experience.html">Experience</a></li>
        <li><a href="projects.html">Projects</a></li>
        <li><a href="contact.html">Contact</a></li>
      </ul>
    </div>
  </nav>

  <main class="hero">
    <div class="hero-container">
      <div class="hero-image">
        <img src="assets/img/headshot-600.jpg" alt="Adam Smith" width="280" height="280">
      </div>
      <div class="hero-content">
        <h1>Adam Smith</h1>
        <p class="hero-title">Software Engineer II at MedShift</p>
        <p class="hero-location">Charlotte, NC</p>
        <p class="hero-intro">I build full-stack applications with Django and Vue.js, and I'm increasingly building <em>with</em> AI rather than just around it. Currently pursuing my M.S. in Computer Science at Clemson while working full-time.</p>
        <div class="hero-actions">
          <a href="assets/adam_smith_resume.pdf" class="button-primary" download>Resume</a>
          <a href="https://github.com/adamruns" class="button-icon" aria-label="GitHub">
            <svg><!-- GitHub SVG icon --></svg>
          </a>
          <a href="https://linkedin.com/in/adamruns" class="button-icon" aria-label="LinkedIn">
            <svg><!-- LinkedIn SVG icon --></svg>
          </a>
        </div>
      </div>
    </div>
  </main>

  <footer class="footer">...</footer>
  <script src="assets/js/main.js"></script>
</body>
</html>
```

Notes:
- Use inline SVGs for GitHub and LinkedIn icons (no icon library dependency). Simple 24x24 SVG paths.
- The nav, footer, and head are repeated on every page (no build tool to extract partials — that's fine for 5 pages).
- Active nav link: on index.html, no nav link is active (home is accessed via the logo).
- `hero-intro` text should feel genuine and human, matching the tone from the GitHub profile README.

**Step 2: Open in browser and verify**

```bash
open /Users/adamsmith/Desktop/Projects/Personal/adamruns.github.io/index.html
```

Verify: headshot displays circular, text layout is correct, nav links work (will 404 until other pages exist, that's fine), responsive at mobile widths.

**Step 3: Commit**

```bash
git add index.html
git commit -m "Add new home page with hero section"
```

---

### Task 4: Shared JavaScript (`assets/js/main.js`)

**Goal:** Mobile nav toggle functionality. Minimal JS — just what's needed.

**Files:**
- Create: `assets/js/main.js`

**Step 1: Write `assets/js/main.js`**

```javascript
function initNavToggle() {
  const toggle = document.querySelector(".nav-toggle");
  const navLinks = document.querySelector(".nav-links");

  if (!toggle || !navLinks) return;

  toggle.addEventListener("click", function () {
    const isOpen = navLinks.classList.toggle("nav-links--open");
    toggle.classList.toggle("nav-toggle--open", isOpen);
    toggle.setAttribute("aria-expanded", isOpen);
  });

  navLinks.addEventListener("click", function (event) {
    if (event.target.tagName === "A") {
      navLinks.classList.remove("nav-links--open");
      toggle.classList.remove("nav-toggle--open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });
}

document.addEventListener("DOMContentLoaded", initNavToggle);
```

**Step 2: Verify mobile nav works**

Open index.html, resize to mobile width, click hamburger, verify menu opens/closes.

**Step 3: Commit**

```bash
git add assets/js/main.js
git commit -m "Add mobile navigation toggle"
```

---

### Task 5: About Page (`about.html`)

**Goal:** Story, tech skills as pills, brief interests section.

**Files:**
- Create: `about.html`

**Step 1: Write `about.html`**

Same head/nav/footer as index.html. The `<a href="about.html">` nav link gets a class `active`.

Main content structure:

```html
<main class="section">
  <div class="container">
    <h1>About Me</h1>

    <div class="about-story">
      <p><!-- Paragraph 1: Origin story — how you got into CS, background --></p>
      <p><!-- Paragraph 2: What you do now — MedShift, full-stack, agentic AI --></p>
      <p><!-- Paragraph 3: M.S. at Clemson while working full-time, what drives you --></p>
    </div>

    <h2>What I Work With</h2>
    <div class="skill-tags">
      <span class="skill-tag">Python</span>
      <span class="skill-tag">TypeScript</span>
      <span class="skill-tag">JavaScript</span>
      <span class="skill-tag">SQL</span>
      <span class="skill-tag">Django</span>
      <span class="skill-tag">Django REST Framework</span>
      <span class="skill-tag">Vue.js</span>
      <span class="skill-tag">React Native</span>
      <span class="skill-tag">PostgreSQL</span>
      <span class="skill-tag">Redis</span>
      <span class="skill-tag">Celery</span>
      <span class="skill-tag">Docker</span>
      <span class="skill-tag">AWS</span>
      <span class="skill-tag">Git</span>
    </div>

    <h2>Outside of Code</h2>
    <p class="about-interests">When I'm not coding, you'll usually find me running, playing soccer or ultimate frisbee, lifting weights, playing guitar, or out with my camera.</p>
  </div>
</main>
```

About copy guidance (for the implementing agent):
- First person, conversational, confident but not boastful
- Paragraph 1: Brief background — grew up doing various forms of development, studied CS at Clemson (Palmetto Fellows, graduated Dec 2024)
- Paragraph 2: Now a Software Engineer II at MedShift in Charlotte — building the Velocity Lending platform with Django and Vue. Led adoption of AI-assisted development across the team. Increasingly building with AI as a true collaborator.
- Paragraph 3: Currently finishing M.S. in CS at Clemson with a focus on AI/ML (4.0 GPA) while working full-time. Motivated by solving real problems and the satisfaction of shipping software that matters.

**Step 2: Open in browser and verify**

Verify: readable text width, skill tags wrap properly, spacing feels balanced, nav "About" link is active.

**Step 3: Commit**

```bash
git add about.html
git commit -m "Add about page with story, skills, and interests"
```

---

### Task 6: Experience Page (`experience.html`)

**Goal:** Work history and education in a clean, scannable timeline layout.

**Files:**
- Create: `experience.html`

**Step 1: Write `experience.html`**

Same head/nav/footer. `experience.html` nav link gets `active` class.

```html
<main class="section">
  <div class="container">
    <h1>Experience</h1>

    <div class="timeline">
      <article class="timeline-entry">
        <div class="timeline-header">
          <h2>MedShift</h2>
          <span class="timeline-date">January 2025 — Present</span>
        </div>
        <p class="timeline-meta">Software Engineer II · Charlotte, NC</p>
        <ul>
          <li>Led a department-wide shift in engineering workflow by introducing and standardizing AI-assisted development, significantly increasing development velocity and team output.</li>
          <li>Designed and built enterprise-grade integrations across third-party financial APIs (QuickBooks, Pipedrive, HubSpot), automating document collection and eliminating hundreds of hours of manual work annually.</li>
        </ul>
        <p class="timeline-meta">Software Engineer I · Jan 2025 — Feb 2026</p>
        <ul>
          <li>Architected features for the Velocity Lending platform (Django/Python, Vue.js/TypeScript) in a small agile team, enabling 30-second loan approvals for high-cost medical devices.</li>
          <li>Resolved a high volume of production bugs and N+1 query performance issues across backend and frontend, improving platform reliability and API response times.</li>
        </ul>
      </article>

      <article class="timeline-entry">
        <div class="timeline-header">
          <h2>Prisma Health — Clemson Senior Capstone</h2>
          <span class="timeline-date">Aug — Dec 2024</span>
        </div>
        <p class="timeline-meta">Senior Capstone Researcher · Clemson, SC</p>
        <ul>
          <li>Selected for a competitive, application-based program to collaborate with Prisma Health on reducing nurse manager burden.</li>
          <li>Designed a custom REST API to transmit synthetic healthcare data to Power BI dashboards, integrating the NASA Task Load Index for workload measurement.</li>
          <li>Built Python data synthesis scripts using Faker and contributed to a React-based Capstone website.</li>
        </ul>
      </article>

      <!-- ScopeStack, Fortis, BoltAffect entries follow same pattern -->
    </div>

    <h2 class="section-subheading">Education</h2>

    <div class="timeline">
      <article class="timeline-entry">
        <div class="timeline-header">
          <h2>Clemson University</h2>
          <span class="timeline-date">Expected May 2026</span>
        </div>
        <p class="timeline-meta">M.S. Computer Science · Clemson, SC</p>
        <ul>
          <li>Bachelor to Graduate Program (4.0 GPA). Focus on Artificial Intelligence and Machine Learning.</li>
          <li>Completed degree concurrently while working full-time as a Software Engineer at MedShift.</li>
        </ul>
      </article>

      <article class="timeline-entry">
        <div class="timeline-header">
          <h2>Clemson University</h2>
          <span class="timeline-date">December 2024</span>
        </div>
        <p class="timeline-meta">B.S. Computer Science · Clemson, SC</p>
        <ul>
          <li>Palmetto Fellows Scholarship Recipient. Participated in 3 hackathons sponsored by AWS.</li>
        </ul>
      </article>
    </div>

    <div class="resume-download">
      <a href="assets/adam_smith_resume.pdf" class="button-primary" download>Download Resume</a>
    </div>
  </div>
</main>
```

All bullet points come directly from the resume PDF. Use the exact text.

**Step 2: Open in browser and verify**

Verify: dates align right on desktop, stack on mobile, left accent border visible, spacing between entries.

**Step 3: Commit**

```bash
git add experience.html
git commit -m "Add experience page with work history and education"
```

---

### Task 7: Projects Page (`projects.html`)

**Goal:** 2-column card grid showcasing best work.

**Files:**
- Create: `projects.html`

**Step 1: Write `projects.html`**

Same head/nav/footer. `projects.html` nav link gets `active` class.

For now, include placeholder projects based on the resume and GitHub. The user can update these later. Use these as starting projects:

1. **Velocity Lending Platform** — "Full-stack fintech platform enabling 30-second loan approvals for medical devices. Built with Django, Vue.js, and TypeScript." Tags: Django, Vue.js, TypeScript, PostgreSQL. No link (proprietary).
2. **AI-Assisted Development Workflows** — "Led adoption of Claude Code as a development environment, building custom skills and orchestrating subagents for agentic development workflows." Tags: Python, Claude Code, AI. Link: GitHub profile.
3. **Traction** — "Cross-platform React Native mobile app deployed to both iOS and Android app stores." Tags: React Native, JavaScript. Links: App Store, Google Play.
4. **Enterprise API Integrations** — "Built integrations across QuickBooks, Pipedrive, and HubSpot APIs, automating document collection for multi-million-dollar asset sales." Tags: Python, Django, REST APIs. No link (proprietary).

Each card:

```html
<article class="project-card">
  <div class="project-card-body">
    <h2>Project Title</h2>
    <p>Description</p>
    <div class="skill-tags">
      <span class="skill-tag">Tag</span>
    </div>
    <a href="..." class="project-link">View Project →</a>
  </div>
</article>
```

Note: No screenshots for now — the cards work fine with just text content. Screenshots can be added later. For cards without external links (proprietary work), omit the link.

**Step 2: Open in browser and verify**

Verify: 2-column grid, cards have hover effect, responsive to single column on mobile, tags display correctly.

**Step 3: Commit**

```bash
git add projects.html
git commit -m "Add projects page with card grid"
```

---

### Task 8: Contact Page (`contact.html`)

**Goal:** Minimal contact page with email and social links.

**Files:**
- Create: `contact.html`

**Step 1: Write `contact.html`**

Same head/nav/footer. `contact.html` nav link gets `active` class.

```html
<main class="section contact">
  <div class="container">
    <h1>Contact</h1>
    <p class="contact-intro">Want to connect? Feel free to reach out.</p>
    <a href="mailto:adamruns27@gmail.com" class="contact-email">adamruns27@gmail.com</a>
    <div class="contact-social">
      <a href="https://github.com/adamruns" aria-label="GitHub"><!-- GitHub SVG --></a>
      <a href="https://linkedin.com/in/adamruns" aria-label="LinkedIn"><!-- LinkedIn SVG --></a>
    </div>
  </div>
</main>
```

**Step 2: Open in browser and verify**

Verify: centered layout, email is clickable mailto link, icons display and link correctly.

**Step 3: Commit**

```bash
git add contact.html
git commit -m "Add contact page"
```

---

### Task 9: Clean Up Old Files

**Goal:** Remove all old template files that are no longer used.

**Step 1: Identify files to remove**

Files to delete:
- `vendor/` directory (Bootstrap, jQuery — no longer needed)
- `assets/css/templatemo-style.css`
- `assets/css/owl.css`
- `assets/css/lightbox.css`
- `assets/css/flex-slider.css`
- `assets/css/fontawesome.css`
- `assets/js/custom.js`
- `assets/js/isotope.min.js`
- `assets/js/owl-carousel.js`
- `assets/js/lightbox.js`
- `assets/fonts/` directory
- `assets/images/` directory (old icons)
- `assets/adam_resume.pdf` (replaced by `adam_smith_resume.pdf`)
- `prepros-6.config`
- Old project screenshot images no longer used (keep `headshot.jpg` and `headshot-600.jpg`)

Files to keep:
- `assets/img/headshot.jpg` and `headshot-600.jpg`
- `assets/adam_smith_resume.pdf`
- `assets/css/style.css`
- `assets/js/main.js`
- All new HTML files
- `docs/` directory
- `.git/`

**Step 2: Remove old files**

```bash
rm -rf vendor/
rm -rf assets/fonts/
rm -rf assets/images/
rm assets/css/templatemo-style.css assets/css/owl.css assets/css/lightbox.css assets/css/flex-slider.css assets/css/fontawesome.css
rm assets/js/custom.js assets/js/isotope.min.js assets/js/owl-carousel.js assets/js/lightbox.js
rm assets/adam_resume.pdf
rm prepros-6.config
```

For old images in `assets/img/`, remove everything except headshot files:

```bash
cd assets/img/
ls  # verify what's there
# Remove all old project screenshots and backgrounds, keeping only headshot*
```

**Step 3: Verify site still works**

Open index.html and all pages, verify nothing is broken.

**Step 4: Commit**

```bash
git add -A
git commit -m "Remove old template files and unused assets"
```

---

### Task 10: CNAME and Final Polish

**Goal:** Set up custom domain, add favicon, final meta tags.

**Step 1: Create CNAME file**

Create `CNAME` in the repo root:

```
adamruns.com
```

**Step 2: Add a simple favicon**

Create a simple SVG favicon (no external dependency):

Create `favicon.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <text y=".9em" font-size="90">A</text>
</svg>
```

Add to the `<head>` of all pages:
```html
<link rel="icon" href="favicon.svg" type="image/svg+xml">
```

**Step 3: Add Open Graph meta tags to all pages**

In the `<head>` of each page, add:
```html
<meta property="og:title" content="Adam Smith — Software Engineer">
<meta property="og:description" content="Software Engineer II at MedShift. Building full-stack applications with Vue, Django, and Python.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://adamruns.com">
```

**Step 4: Verify all pages**

Open every page, check all links work, check mobile responsiveness, check that all content is correct.

**Step 5: Commit**

```bash
git add CNAME favicon.svg index.html about.html experience.html projects.html contact.html
git commit -m "Add CNAME for adamruns.com, favicon, and Open Graph tags"
```

---

## Cloudflare DNS Setup (Manual — Not Automated)

After pushing to GitHub, the user needs to configure Cloudflare DNS:

1. In Cloudflare dashboard for adamruns.com, add DNS records:
   - Type: `CNAME`, Name: `@`, Target: `adamruns.github.io`, Proxy: DNS only (gray cloud)
   - Type: `CNAME`, Name: `www`, Target: `adamruns.github.io`, Proxy: DNS only (gray cloud)
2. In GitHub repo Settings → Pages:
   - Source: Deploy from branch (master)
   - Custom domain: `adamruns.com`
   - Check "Enforce HTTPS" once DNS propagates

---

## Task Summary

| Task | Description | Key Files |
|------|-------------|-----------|
| 1 | Copy assets (headshot, resume) | `assets/img/headshot*.jpg`, `assets/adam_smith_resume.pdf` |
| 2 | CSS design system | `assets/css/style.css` |
| 3 | Home page | `index.html` |
| 4 | Shared JavaScript | `assets/js/main.js` |
| 5 | About page | `about.html` |
| 6 | Experience page | `experience.html` |
| 7 | Projects page | `projects.html` |
| 8 | Contact page | `contact.html` |
| 9 | Clean up old files | Remove `vendor/`, old CSS/JS/images |
| 10 | CNAME, favicon, OG tags | `CNAME`, `favicon.svg`, all HTML |
