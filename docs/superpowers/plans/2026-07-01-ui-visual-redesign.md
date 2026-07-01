# UI Visual Redesign + Landing Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the YouTube-to-MIDI web app a polished, colorful, professional visual identity, and add a landing/splash page that explains the tool before the user enters the app.

**Architecture:** Pure front-end styling/markup change. All work happens in the three existing static files (`static/index.html`, `static/styles.css`, `static/app.js`) — no backend routes, no build step, no new dependencies beyond two Google Fonts `<link>` tags. A new `landing` value is added to the existing Alpine.js `activeView` state machine; every other view (`form`, `progress`, `stems`, `midi`) keeps its current structure and gets restyled in place.

**Tech Stack:** Alpine.js 3 (existing CDN script, unchanged), plain CSS (no preprocessor, no framework), Google Fonts (Inter + Space Grotesk), FastAPI static file serving (unchanged).

## Global Constraints

- No build step and no test suite exist in this project (per `CLAUDE.md`) — verification in this plan is done via `grep` structural checks, `node --check` for JS syntax, and a final manual browser walkthrough. There is no way to automate visual/pixel verification here.
- All changes confined to `static/index.html`, `static/styles.css`, `static/app.js`. Do not touch backend files (`server/**`).
- Color palette (from spec): background `#0b0b0f` (page) / `#15151c` (panel) / `#1c1c26` (elevated card), border `#2a2a35`, text primary `#e8e8ec`, text muted `#9a9aa5`, primary accent gradient `#8b5cf6` → `#ec4899`, secondary accent `#22d3ee`, success `#16a34a` / hover `#15803d`, error `#f87171`, warning `#f59e0b` (reserved, not used yet).
- Typography (from spec): headings use `'Space Grotesk', system-ui, sans-serif`, body/UI uses `'Inter', system-ui, sans-serif`, loaded via Google Fonts `<link>` tags in `index.html`.
- The landing page shows on every page load (`init()`), not just first-run, per the approved spec.
- Keep the existing sidebar + main-panel structural layout — this is a styling/polish pass, not a layout rewrite.
- The dev server is started with `python run_server.py` (FastAPI + uvicorn, serves `/` → `static/index.html`, `/static/*` → static files). `node` and `python` are both available in this environment for verification commands.

---

### Task 1: Foundation — color system & typography

**Files:**
- Modify: `static/index.html:1-10` (head section)
- Modify: `static/styles.css:1-11` (top of file)
- Modify: `static/styles.css:264-265` (bottom of file, `h1, h2` rule)

**Interfaces:**
- Produces: CSS custom properties on `:root` — `--bg-page`, `--bg-panel`, `--bg-elevated`, `--border`, `--text-primary`, `--text-muted`, `--accent-1`, `--accent-2`, `--accent-gradient`, `--accent-cyan`, `--success`, `--success-hover`, `--error`, `--warning`, `--radius`, `--font-heading`, `--font-body`. Every later task consumes these instead of hardcoded hex colors.

- [ ] **Step 1: Add Google Fonts links to `index.html`**

In `static/index.html`, replace:

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>YouTube to MIDI</title>
  <link rel="stylesheet" href="/static/styles.css">
  <script defer src="/static/app.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
```

with:

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>YouTube to MIDI</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/styles.css">
  <script defer src="/static/app.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
```

- [ ] **Step 2: Add the `:root` color/typography variables and update the base `body` rule in `styles.css`**

Replace:

```css
/* static/styles.css */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: system-ui, sans-serif;
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #0f0f0f;
  color: #e0e0e0;
}
```

with:

```css
/* static/styles.css */
:root {
  --bg-page: #0b0b0f;
  --bg-panel: #15151c;
  --bg-elevated: #1c1c26;
  --border: #2a2a35;
  --text-primary: #e8e8ec;
  --text-muted: #9a9aa5;
  --accent-1: #8b5cf6;
  --accent-2: #ec4899;
  --accent-gradient: linear-gradient(135deg, var(--accent-1), var(--accent-2));
  --accent-cyan: #22d3ee;
  --success: #16a34a;
  --success-hover: #15803d;
  --error: #f87171;
  --warning: #f59e0b;
  --radius: 10px;
  --font-heading: 'Space Grotesk', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font-body);
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-page);
  color: var(--text-primary);
}
```

- [ ] **Step 3: Update the heading rule at the bottom of `styles.css` to use the new heading font**

Replace:

```css
h1, h2 { margin-bottom: 24px; }
h2 { font-size: 18px; }
```

with:

```css
h1, h2, h3 { font-family: var(--font-heading); }
h1, h2 { margin-bottom: 24px; }
h2 { font-size: 20px; font-weight: 600; }
```

- [ ] **Step 4: Verify**

Run:

```bash
grep -n "fonts.googleapis.com" static/index.html
grep -n -- "--accent-gradient" static/styles.css
grep -n "font-family: var(--font-body)" static/styles.css
grep -n "font-family: var(--font-heading)" static/styles.css
```

Expected: each command prints at least one matching line (no empty output).

- [ ] **Step 5: Commit**

```bash
git add static/index.html static/styles.css
git commit -m "feat(ui): add color system and typography foundation"
```

---

### Task 2: Landing page (structure, navigation, styling)

**Files:**
- Modify: `static/index.html:11-30` (body start / sidebar)
- Modify: `static/app.js` (`activeView` initial value, add `getStarted()` / `goHome()` methods)
- Modify: `static/styles.css` (insert new "Landing page" section, update `#sidebar-header`)

**Interfaces:**
- Consumes: `--bg-page`, `--bg-elevated`, `--border`, `--text-muted`, `--accent-gradient`, `--font-heading`, `--radius` (from Task 1).
- Produces: `appRoot().getStarted()` — no args, navigates to the most recent job if `this.jobs.length > 0` (via existing `selectJob(job)`), else calls existing `newJob()`. `appRoot().goHome()` — no args, closes any open SSE connection and sets `this.activeView = 'landing'`. Later tasks (sidebar polish) style the `#sidebar-logo` element this task introduces but do not change its markup or these two methods.

- [ ] **Step 1: Add the landing page markup and gate the sidebar/main panel behind `activeView !== 'landing'`**

In `static/index.html`, replace:

```html
<body x-data="appRoot()" x-init="init()">

  <!-- Sidebar -->
  <aside id="sidebar">
    <div id="sidebar-header">
      <button @click="newJob()">+ New Job</button>
    </div>
    <div id="job-list">
      <template x-for="job in jobs" :key="job.id">
        <div class="job-item" :class="{ active: job.id === activeJobId }"
             @click="selectJob(job)">
          <span class="job-name" x-text="job.name"></span>
          <span class="status-icon" x-text="statusIcon(job.status)"></span>
        </div>
      </template>
    </div>
  </aside>

  <!-- Main panel -->
  <main id="main">
```

with:

```html
<body x-data="appRoot()" x-init="init()">

  <!-- Landing page -->
  <div id="landing-page" x-show="activeView === 'landing'">
    <div id="landing-hero">
      <div id="landing-logo">YT<span>2</span>MIDI</div>
      <h1 id="landing-headline">Turn any YouTube video into MIDI</h1>
      <p id="landing-subhead">Download the audio, split it into stems, and convert the part you want into a playable MIDI file — all in one pipeline.</p>
      <button id="landing-cta" @click="getStarted()">Get Started</button>
    </div>
    <div id="landing-steps">
      <div class="landing-step">
        <div class="landing-step-icon">⬇</div>
        <h3>Download</h3>
        <p>yt-dlp pulls the audio track straight from a YouTube URL.</p>
      </div>
      <div class="landing-step">
        <div class="landing-step-icon">🎚</div>
        <h3>Separate</h3>
        <p>Demucs isolates vocals, bass, drums, and other instruments into individual stems.</p>
      </div>
      <div class="landing-step">
        <div class="landing-step-icon">🎹</div>
        <h3>Convert</h3>
        <p>Basic Pitch turns the stem you pick into a downloadable .mid file.</p>
      </div>
    </div>
    <div id="landing-credits">Built on yt-dlp, Demucs, and Basic Pitch.</div>
  </div>

  <!-- Sidebar -->
  <aside id="sidebar" x-show="activeView !== 'landing'">
    <div id="sidebar-header">
      <div id="sidebar-logo" @click="goHome()" title="Back to home">YT<span>2</span>MIDI</div>
      <button @click="newJob()">+ New Job</button>
    </div>
    <div id="job-list">
      <template x-for="job in jobs" :key="job.id">
        <div class="job-item" :class="{ active: job.id === activeJobId }"
             @click="selectJob(job)">
          <span class="job-name" x-text="job.name"></span>
          <span class="status-icon" x-text="statusIcon(job.status)"></span>
        </div>
      </template>
    </div>
  </aside>

  <!-- Main panel -->
  <main id="main" x-show="activeView !== 'landing'">
```

- [ ] **Step 2: Set the default view to `landing` and add navigation methods in `app.js`**

Replace:

```javascript
    activeView: 'form',  // 'form' | 'progress' | 'stems' | 'midi'
```

with:

```javascript
    activeView: 'landing',  // 'landing' | 'form' | 'progress' | 'stems' | 'midi'
```

Then replace:

```javascript
    newJob() {
      this.activeJobId = null;
      this.activeView = 'form';
      this.convertError = null;
      if (this._evtSource) { this._evtSource.close(); this._evtSource = null; }
    },
```

with:

```javascript
    newJob() {
      this.activeJobId = null;
      this.activeView = 'form';
      this.convertError = null;
      if (this._evtSource) { this._evtSource.close(); this._evtSource = null; }
    },

    getStarted() {
      if (this.jobs.length > 0) {
        this.selectJob(this.jobs[0]);
      } else {
        this.newJob();
      }
    },

    goHome() {
      if (this._evtSource) { this._evtSource.close(); this._evtSource = null; }
      this.activeView = 'landing';
    },
```

- [ ] **Step 3: Add landing page CSS and basic `#sidebar-logo` styling**

In `static/styles.css`, replace:

```css
body {
  font-family: var(--font-body);
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-page);
  color: var(--text-primary);
}

/* Sidebar */
```

with:

```css
body {
  font-family: var(--font-body);
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-page);
  color: var(--text-primary);
}

/* Landing page */
#landing-page {
  width: 100%;
  height: 100vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 24px 48px;
  text-align: center;
  background:
    radial-gradient(circle at 20% 20%, rgba(139, 92, 246, 0.15), transparent 40%),
    radial-gradient(circle at 80% 0%, rgba(236, 72, 153, 0.12), transparent 40%),
    var(--bg-page);
}

#landing-hero { max-width: 640px; }

#landing-logo {
  display: inline-block;
  font-family: var(--font-heading);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-bottom: 32px;
}
#landing-logo span { color: transparent; background: var(--accent-gradient); -webkit-background-clip: text; background-clip: text; }

#landing-headline {
  font-family: var(--font-heading);
  font-size: 40px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 16px;
}

#landing-subhead {
  font-size: 16px;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 32px;
}

#landing-cta {
  padding: 14px 32px;
  font-size: 15px;
  font-weight: 600;
  color: white;
  background: var(--accent-gradient);
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.35);
}
#landing-cta:hover { filter: brightness(1.08); }

#landing-steps {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  justify-content: center;
  max-width: 900px;
  margin-top: 64px;
}

.landing-step {
  width: 240px;
  padding: 24px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.landing-step-icon { font-size: 28px; margin-bottom: 12px; }
.landing-step h3 { font-size: 16px; margin-bottom: 8px; }
.landing-step p { font-size: 13px; color: var(--text-muted); line-height: 1.5; }

#landing-credits {
  margin-top: 48px;
  font-size: 12px;
  color: var(--text-muted);
}

/* Sidebar */
```

Then replace:

```css
#sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #2e2e2e;
}
```

with:

```css
#sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

#sidebar-logo {
  font-family: var(--font-heading);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  cursor: pointer;
}
#sidebar-logo span { color: transparent; background: var(--accent-gradient); -webkit-background-clip: text; background-clip: text; }
```

- [ ] **Step 4: Verify**

Run:

```bash
node --check static/app.js
grep -n "id=\"landing-page\"" static/index.html
grep -n "getStarted()" static/app.js
grep -n "goHome()" static/app.js
grep -n "#landing-cta" static/styles.css
```

Expected: `node --check` produces no output (valid syntax), all `grep` commands print a matching line.

- [ ] **Step 5: Commit**

```bash
git add static/index.html static/app.js static/styles.css
git commit -m "feat(ui): add landing page with navigation to/from the app"
```

---

### Task 3: Sidebar visual polish

**Files:**
- Modify: `static/index.html` (add status class binding to job status icon)
- Modify: `static/styles.css` (`#sidebar`, `#sidebar-header button`, `.job-item`, `.status-icon`)

**Interfaces:**
- Consumes: CSS variables from Task 1; does not touch `#sidebar-logo` or `#landing-*` rules from Task 2.

- [ ] **Step 1: Add a status class to the job status icon**

In `static/index.html`, replace:

```html
          <span class="status-icon" x-text="statusIcon(job.status)"></span>
```

with:

```html
          <span class="status-icon" :class="'status-' + job.status" x-text="statusIcon(job.status)"></span>
```

- [ ] **Step 2: Restyle the sidebar container and New Job button**

In `static/styles.css`, replace:

```css
#sidebar {
  width: 240px;
  min-width: 240px;
  background: #1a1a1a;
  border-right: 1px solid #2e2e2e;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
```

with:

```css
#sidebar {
  width: 240px;
  min-width: 240px;
  background: var(--bg-panel);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
```

Then replace:

```css
#sidebar-header button {
  width: 100%;
  padding: 8px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

#sidebar-header button:hover { background: #1d4ed8; }
```

with:

```css
#sidebar-header button {
  width: 100%;
  padding: 10px;
  background: var(--accent-gradient);
  color: white;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

#sidebar-header button:hover { filter: brightness(1.08); }
```

- [ ] **Step 3: Restyle job list rows and status colors**

Replace:

```css
.job-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  gap: 8px;
}

.job-item:hover { background: #252525; }
.job-item.active { background: #1e3a5f; }

.job-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-icon { font-size: 14px; flex-shrink: 0; }
```

with:

```css
.job-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 13px;
  gap: 8px;
  border-left: 3px solid transparent;
}

.job-item:hover { background: var(--bg-elevated); }
.job-item.active {
  background: var(--bg-elevated);
  border-left: 3px solid var(--accent-1);
}

.job-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-icon { font-size: 14px; flex-shrink: 0; }
.status-icon.status-pending { color: var(--text-muted); }
.status-icon.status-running { color: var(--accent-cyan); }
.status-icon.status-completed { color: var(--success); }
.status-icon.status-failed { color: var(--error); }
```

- [ ] **Step 4: Verify**

Run:

```bash
grep -n "status-' + job.status" static/index.html
grep -n "border-left: 3px solid var(--accent-1)" static/styles.css
grep -n "status-icon.status-running" static/styles.css
```

Expected: each prints a matching line.

- [ ] **Step 5: Commit**

```bash
git add static/index.html static/styles.css
git commit -m "feat(ui): restyle sidebar with gradient accents and status colors"
```

---

### Task 4: Form view polish

**Files:**
- Modify: `static/index.html` (wrap form fields in a card, swap inline error style for a class)
- Modify: `static/styles.css` (`/* Form */` section)

**Interfaces:**
- Consumes: CSS variables from Task 1. Produces: `.error-text` utility class, reused by Task 6 for the stem-browser error message.

- [ ] **Step 1: Wrap the form fields in a card and use a shared error class**

In `static/index.html`, replace:

```html
    <!-- Form view -->
    <div x-show="activeView === 'form'">
      <h2>New Job</h2>

      <div class="form-group">
```

with:

```html
    <!-- Form view -->
    <div x-show="activeView === 'form'">
      <h2>New Job</h2>

      <div class="form-card">
      <div class="form-group">
```

Then replace:

```html
      <button class="btn-primary"
              @click="submitJob()"
              :disabled="!form.url || !form.name || form.splitters.length === 0">
        Run Pipeline
      </button>

      <div x-show="convertError" style="color: #f87171; margin-top: 12px;" x-text="convertError"></div>
    </div>
```

with:

```html
      <button class="btn-primary"
              @click="submitJob()"
              :disabled="!form.url || !form.name || form.splitters.length === 0">
        Run Pipeline
      </button>
      </div>

      <div x-show="convertError" class="error-text" x-text="convertError"></div>
    </div>
```

- [ ] **Step 2: Restyle the form section in `styles.css`**

Replace:

```css
/* Form */
.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-size: 13px; color: #aaa; margin-bottom: 6px; }
.form-group input[type="text"],
.form-group input[type="url"] {
  width: 100%;
  max-width: 560px;
  padding: 10px 12px;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 6px;
  color: #e0e0e0;
  font-size: 14px;
}

.splitter-options { display: flex; gap: 12px; flex-wrap: wrap; }
.splitter-options label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #e0e0e0;
}
.splitter-options label.disabled { opacity: 0.4; cursor: not-allowed; }

.speed-options { display: flex; gap: 16px; }
.speed-options label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  cursor: pointer;
  color: #e0e0e0;
}

.btn-primary {
  padding: 10px 24px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}
.btn-primary:hover { background: #1d4ed8; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
```

with:

```css
/* Form */
.form-card {
  max-width: 560px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.form-group { margin-bottom: 20px; }
.form-group:last-child { margin-bottom: 0; }
.form-group label { display: block; font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }
.form-group input[type="text"],
.form-group input[type="url"] {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  transition: box-shadow 0.15s, border-color 0.15s;
}
.form-group input[type="text"]:focus,
.form-group input[type="url"]:focus {
  outline: none;
  border-color: var(--accent-1);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.25);
}

.splitter-options { display: flex; gap: 10px; flex-wrap: wrap; }
.splitter-options label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-primary);
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--bg-page);
  transition: border-color 0.15s, background 0.15s;
}
.splitter-options label:has(input:checked) {
  border-color: var(--accent-1);
  background: rgba(139, 92, 246, 0.12);
}
.splitter-options label.disabled { opacity: 0.4; cursor: not-allowed; }

.speed-options { display: inline-flex; gap: 2px; padding: 4px; background: var(--bg-page); border: 1px solid var(--border); border-radius: 999px; }
.speed-options label {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  cursor: pointer;
  color: var(--text-muted);
  padding: 6px 14px;
  border-radius: 999px;
  transition: background 0.15s, color 0.15s;
}
.speed-options label:has(input:checked) {
  background: var(--accent-gradient);
  color: white;
}
.speed-options input[type="radio"] { position: absolute; opacity: 0; pointer-events: none; }

.btn-primary {
  padding: 10px 24px;
  background: var(--accent-gradient);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.btn-primary:hover { filter: brightness(1.08); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; filter: none; }

.error-text { color: var(--error); margin-top: 12px; font-size: 13px; }
```

- [ ] **Step 3: Verify**

Run:

```bash
grep -n "class=\"form-card\"" static/index.html
grep -n "class=\"error-text\"" static/index.html
grep -n "splitter-options label:has" static/styles.css
grep -n "speed-options label:has" static/styles.css
```

Expected: each prints a matching line.

- [ ] **Step 4: Commit**

```bash
git add static/index.html static/styles.css
git commit -m "feat(ui): restyle new-job form as a card with chip/segmented controls"
```

---

### Task 5: Progress view polish (vertical stepper)

**Files:**
- Modify: `static/index.html` (status class binding on step icon)
- Modify: `static/styles.css` (`/* Progress */` section)

**Interfaces:**
- Consumes: CSS variables from Task 1.

- [ ] **Step 1: Add a status class to the step icon**

In `static/index.html`, replace:

```html
            <span class="step-icon" x-text="stepIcon(step.status)"></span>
```

with:

```html
            <span class="step-icon" :class="'status-' + step.status" x-text="stepIcon(step.status)"></span>
```

- [ ] **Step 2: Restyle the progress step list as a connected vertical stepper**

In `static/styles.css`, replace:

```css
/* Progress */
.step-list { list-style: none; margin-top: 16px; }
.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #222;
  font-size: 14px;
}
.step-icon { width: 20px; text-align: center; }
.step-error {
  font-size: 12px;
  color: #f87171;
  margin-top: 4px;
  white-space: pre-wrap;
  cursor: pointer;
}
```

with:

```css
/* Progress */
.step-list { list-style: none; margin-top: 24px; position: relative; }

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 0 0 24px;
  font-size: 14px;
  position: relative;
}
.step-item:last-child { padding-bottom: 0; }

.step-item::before {
  content: '';
  position: absolute;
  left: 13px;
  top: 28px;
  bottom: 0;
  width: 2px;
  background: var(--border);
}
.step-item:last-child::before { display: none; }

.step-icon {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  color: var(--text-muted);
  z-index: 1;
}
.step-icon.status-running {
  color: var(--accent-cyan);
  border-color: var(--accent-cyan);
  animation: step-spin 1.2s linear infinite;
}
.step-icon.status-completed { color: var(--success); border-color: var(--success); }
.step-icon.status-failed { color: var(--error); border-color: var(--error); }

@keyframes step-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.step-item > div { padding-top: 4px; }

.step-error {
  font-size: 12px;
  color: var(--error);
  margin-top: 4px;
  white-space: pre-wrap;
  cursor: pointer;
}
```

- [ ] **Step 3: Verify**

Run:

```bash
grep -n "status-' + step.status" static/index.html
grep -n "step-spin" static/styles.css
grep -n "step-icon.status-running" static/styles.css
```

Expected: each prints a matching line.

- [ ] **Step 4: Commit**

```bash
git add static/index.html static/styles.css
git commit -m "feat(ui): restyle pipeline progress as a connected vertical stepper"
```

---

### Task 6: Stem browser polish

**Files:**
- Modify: `static/index.html` (swap inline error style for the `.error-text` class)
- Modify: `static/styles.css` (`/* Stem browser */` and `/* Global scrubber */` sections)

**Interfaces:**
- Consumes: `.error-text` (from Task 4), CSS variables from Task 1.

- [ ] **Step 1: Use the shared error class in the stem browser view**

In `static/index.html`, replace:

```html
      <!-- Error from conversion attempt -->
      <div x-show="convertError" style="color: #f87171; margin-top: 12px;" x-text="convertError"></div>
```

with:

```html
      <!-- Error from conversion attempt -->
      <div x-show="convertError" class="error-text" x-text="convertError"></div>
```

- [ ] **Step 2: Restyle stem rows as cards and pill-badge the splitter label**

In `static/styles.css`, replace:

```css
/* Stem browser */
.stem-section { margin-bottom: 32px; }
.stem-section h3 {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #888;
  margin-bottom: 12px;
}

.stem-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #1e1e1e;
}

.stem-row .splitter-label {
  width: 120px;
  font-size: 13px;
  color: #aaa;
  flex-shrink: 0;
}

.stem-row button {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: #2563eb;
  color: white;
  font-size: 16px;
  cursor: pointer;
  flex-shrink: 0;
}

.stem-row button:hover { background: #1d4ed8; }

.stem-row .time-display {
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  color: #888;
  width: 48px;
}

.stem-row .pick-btn {
  margin-left: auto;
  padding: 6px 14px;
  background: #16a34a;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
}
.stem-row .pick-btn:hover { background: #15803d; }
.stem-row.selected-stem { background: #0f2a1a; border-radius: 6px; }
```

with:

```css
/* Stem browser */
.stem-section { margin-bottom: 32px; }
.stem-section h3 {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.stem-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 8px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: border-color 0.15s;
}
.stem-row:hover { border-color: var(--accent-1); }

.stem-row .splitter-label {
  width: 96px;
  font-size: 12px;
  color: var(--text-muted);
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--bg-page);
  border: 1px solid var(--border);
  text-align: center;
}

.stem-row button {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: var(--accent-gradient);
  color: white;
  font-size: 16px;
  cursor: pointer;
  flex-shrink: 0;
}

.stem-row button:hover { filter: brightness(1.08); }

.stem-row .time-display {
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  color: var(--text-muted);
  width: 48px;
}

.stem-row .pick-btn {
  margin-left: auto;
  padding: 6px 14px;
  background: var(--success);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
}
.stem-row .pick-btn:hover { background: var(--success-hover); }
.stem-row.selected-stem { border-color: var(--accent-cyan); background: rgba(34, 211, 238, 0.08); }
```

- [ ] **Step 3: Restyle the global scrubber bar**

Replace:

```css
/* Global scrubber */
#scrubber-bar {
  position: sticky;
  bottom: 0;
  background: #111;
  border-top: 1px solid #2e2e2e;
  padding: 12px 0;
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.scrubber-main {
  flex: 1;
}

.scrubber-main input[type="range"] {
  width: 100%;
  accent-color: #2563eb;
}

.scrubber-times {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.volume-icon {
  font-size: 14px;
}

.volume-control input[type="range"] {
  width: 100px;
  accent-color: #2563eb;
}
```

with:

```css
/* Global scrubber */
#scrubber-bar {
  position: sticky;
  bottom: 0;
  background: var(--bg-panel);
  border-top: 1px solid var(--border);
  padding: 16px;
  margin-top: 16px;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  gap: 16px;
}

.scrubber-main {
  flex: 1;
}

.scrubber-main input[type="range"] {
  width: 100%;
  accent-color: var(--accent-1);
}

.scrubber-times {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.volume-icon {
  font-size: 14px;
}

.volume-control input[type="range"] {
  width: 100px;
  accent-color: var(--accent-1);
}
```

- [ ] **Step 4: Verify**

Run:

```bash
grep -n "class=\"error-text\"" static/index.html
grep -n "stem-row:hover" static/styles.css
grep -n "accent-color: var(--accent-1)" static/styles.css
```

Expected: each prints matching line(s) (the last one should match twice — scrubber and volume slider).

- [ ] **Step 5: Commit**

```bash
git add static/index.html static/styles.css
git commit -m "feat(ui): restyle stem browser rows as cards and unify error styling"
```

---

### Task 7: MIDI download view polish

**Files:**
- Modify: `static/index.html` (`activeView === 'midi'` block)
- Modify: `static/styles.css` (`/* MIDI view */` section)

**Interfaces:**
- Consumes: CSS variables from Task 1.

- [ ] **Step 1: Add a success icon and drop inline styles from the MIDI view markup**

In `static/index.html`, replace:

```html
    <!-- MIDI download view -->
    <div x-show="activeView === 'midi'">
      <h2>MIDI Ready</h2>
      <p style="color: #aaa; font-size: 14px; margin-bottom: 16px;">
        Basic Pitch conversion complete. Download your files below.
      </p>
      <div class="download-links">
        <a :href="midiInfo ? '/audio/midi/' + midiInfo.jobId : '#'"
           class="dl-midi" download>
          ⬇ Download MIDI (.mid)
        </a>
        <a :href="midiInfo && midiInfo.stemId ? '/audio/stem/' + midiInfo.stemId : '#'"
           class="dl-wav" download>
          ⬇ Download Stem WAV
        </a>
      </div>
      <div style="margin-top: 32px;">
        <button class="btn-primary" @click="activeView = 'stems'">← Back to stems</button>
      </div>
    </div>
```

with:

```html
    <!-- MIDI download view -->
    <div x-show="activeView === 'midi'">
      <div class="midi-success-icon">✓</div>
      <h2>MIDI Ready</h2>
      <p class="midi-subtext">
        Basic Pitch conversion complete. Download your files below.
      </p>
      <div class="download-links">
        <a :href="midiInfo ? '/audio/midi/' + midiInfo.jobId : '#'"
           class="dl-midi" download>
          ⬇ Download MIDI (.mid)
        </a>
        <a :href="midiInfo && midiInfo.stemId ? '/audio/stem/' + midiInfo.stemId : '#'"
           class="dl-wav" download>
          ⬇ Download Stem WAV
        </a>
      </div>
      <div class="midi-back-row">
        <button class="btn-primary" @click="activeView = 'stems'">← Back to stems</button>
      </div>
    </div>
```

- [ ] **Step 2: Restyle the MIDI view in `styles.css`**

Replace:

```css
/* MIDI view */
.download-links { display: flex; gap: 16px; margin-top: 24px; flex-wrap: wrap; }
.download-links a {
  padding: 10px 20px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
}
.dl-midi { background: #7c3aed; color: white; }
.dl-midi:hover { background: #6d28d9; }
.dl-wav  { background: #374151; color: white; }
.dl-wav:hover  { background: #1f2937; }
```

with:

```css
/* MIDI view */
.midi-success-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(22, 163, 74, 0.15);
  color: var(--success);
  border: 2px solid var(--success);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-bottom: 16px;
}

.midi-subtext { color: var(--text-muted); font-size: 14px; margin-bottom: 16px; }
.midi-back-row { margin-top: 32px; }

.download-links { display: flex; gap: 16px; margin-top: 24px; flex-wrap: wrap; }
.download-links a {
  padding: 10px 20px;
  border-radius: var(--radius);
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
}
.dl-midi { background: var(--accent-gradient); color: white; }
.dl-midi:hover { filter: brightness(1.08); }
.dl-wav  { background: var(--bg-elevated); border: 1px solid var(--border); color: var(--text-primary); }
.dl-wav:hover  { border-color: var(--accent-1); }
```

- [ ] **Step 3: Verify**

Run:

```bash
grep -n "midi-success-icon" static/index.html
grep -n "midi-success-icon" static/styles.css
grep -n "dl-midi { background: var(--accent-gradient)" static/styles.css
```

Expected: each prints a matching line.

- [ ] **Step 4: Commit**

```bash
git add static/index.html static/styles.css
git commit -m "feat(ui): restyle MIDI download view with success state and gradient CTA"
```

---

### Task 8: Full visual QA pass

**Files:** None (verification only; fix-forward if issues are found).

**Interfaces:** None — this task exercises every view produced by Tasks 1–7 together.

- [ ] **Step 1: Start the dev server**

```bash
python run_server.py
```

Run this with the background-process option your tool provides (e.g. `run_in_background: true`), since it runs until stopped.

- [ ] **Step 2: Manually walk through the app in a browser at `http://127.0.0.1:8000/`**

Confirm each item:

- [ ] Landing page loads first: gradient wordmark, headline, subhead, "Get Started" button, 3-step explanation cards, credits line. No sidebar is visible on this screen.
- [ ] Clicking "Get Started" with no existing jobs opens the New Job form (card-styled, chip-style splitter checkboxes, segmented speed control, gradient "Run Pipeline" button) and the sidebar appears with the gradient "+ New Job" button and clickable `YT2MIDI` wordmark.
- [ ] Submitting a job switches to the progress view: steps render as a connected vertical stepper, the currently-running step's icon is cyan and animating, completed steps are green, failed steps are red with the error message visible in red text below the label.
- [ ] Once a job completes, the stem browser shows each stem type section with stem rows as cards, splitter name as a pill badge, working play/pause button, scrubber, and volume slider all tinted with the new accent color.
- [ ] Clicking "Convert to MIDI" on a stem shows the MIDI Ready view with a green success icon and gradient "Download MIDI" button.
- [ ] Clicking the sidebar `YT2MIDI` wordmark from any view returns to the landing page.
- [ ] Reloading the page (`F5`) always returns to the landing page, per spec, even with existing jobs in the sidebar.
- [ ] Selecting an existing job from the sidebar list shows a colored left accent bar and highlighted background on the active job item, and a colored status dot/icon matching its status.
- [ ] No leftover flat colors from the old theme (`#2563eb`, `#0f0f0f`, `#1a1a1a`) are visible anywhere — everything uses the new dark palette and purple-pink gradient accent.

If any item fails, fix it directly in the relevant file from Tasks 1–7, re-check the item, then commit the fix with a message describing what was wrong (e.g. `git commit -m "fix(ui): correct stem row hover color"`).

- [ ] **Step 3: Stop the dev server**

Stop the background process started in Step 1.

- [ ] **Step 4: Final confirmation**

```bash
git log --oneline -8
git status
```

Expected: the 7 feature commits from Tasks 1–7 (plus any fix-forward commits from Step 2) are present, and `git status` shows a clean working tree for `static/*` (no uncommitted changes).
