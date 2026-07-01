# UI Visual Redesign + Landing Page

Date: 2026-07-01

## Problem

The frontend (`static/index.html`, `static/styles.css`, `static/app.js`) is functional but visually plain: flat dark theme, a single flat blue accent color, system font, no explanation of what the tool does before you're dropped into a "New Job" form. The goal is a more polished, professional, colorful look, plus a landing/splash page that explains the tool before entering the app.

## Scope

- Visual/styling redesign only. No changes to the sidebar + main-panel structural layout, no new backend routes, no build step introduced.
- Add one new view state (`landing`) to the existing Alpine `appRoot()` app, plus supporting markup/CSS.
- All changes confined to `static/index.html`, `static/styles.css`, `static/app.js`.

## 1. Landing Page

- New `activeView === 'landing'` state. On every page load (`init()`), the app starts on `landing` regardless of whether jobs already exist — landing is shown every time, not just first-run.
- Content, top to bottom:
  - Hero: wordmark/logo text, headline ("Turn any YouTube video into MIDI"), one-line subhead, a gradient-styled "Get Started" button.
  - "How it works": 3 steps with icons/labels — **Download** (yt-dlp pulls audio), **Separate** (Demucs isolates vocals/bass/drums/other stems), **Convert** (Basic Pitch turns the chosen stem into a `.mid` file).
  - Credits line: small text noting the tool is built on yt-dlp, Demucs, and Basic Pitch.
- "Get Started" navigates into the existing app: show the last active job if one exists (re-run `selectJob` logic against the most recent job in `jobs`), otherwise show the New Job form (`activeView = 'form'`).
- The sidebar header shows a clickable logo/wordmark that sets `activeView = 'landing'` to return to the splash screen at any time. The sidebar itself is hidden while `activeView === 'landing'` (landing is full-page, no sidebar/job list visible).

## 2. Visual System

**Color palette** (replaces current flat dark/blue theme):
- Background: `#0b0b0f` (page), `#15151c` (panels/sidebar), `#1c1c26` (elevated cards/rows)
- Borders: `#2a2a35` (replaces `#2e2e2e`/`#333`)
- Primary accent: purple→pink gradient, `#8b5cf6` → `#ec4899`, used for primary buttons (New Job, Get Started, Run Pipeline, Convert to MIDI, MIDI download), active states, focus rings
- Secondary accent: cyan `#22d3ee`, used sparingly for links/secondary highlights
- Semantic: success/download-WAV green `#16a34a` (existing), error `#f87171` (existing), warning amber `#f59e0b` if a warning state is ever needed
- Text: primary `#e8e8ec`, secondary/muted `#9a9aa5` (replaces `#aaa`/`#888`/`#666`)

**Typography**:
- Load "Space Grotesk" (headings, hero, section titles) and "Inter" (body/UI text, labels, inputs) via Google Fonts `<link>` tags in `index.html`.
- Body font-family becomes `'Inter', system-ui, sans-serif`; headings use `'Space Grotesk', system-ui, sans-serif`.

## 3. Component Polish

Structure (sidebar + main panel + views) is unchanged; only styling and small presentational markup additions:

- **Sidebar**: logo/wordmark in `#sidebar-header` (click → landing), "New Job" button gets the gradient treatment, job items get a small colored status dot (replacing/augmenting the current icon) and a left accent bar (gradient) when active.
- **Form view**: form groups wrapped in a card surface (`#1c1c26`, border, radius, subtle shadow), inputs get a glowing focus ring (accent color box-shadow on `:focus`), splitter checkboxes restyled as toggle chips, speed radio options restyled as a segmented control.
- **Progress view**: step list becomes a vertical stepper with a connecting line between steps; status icons get distinct colors (pending muted gray, running cyan with a subtle CSS spin animation, completed green check, failed red x).
- **Stem browser**: each stem row becomes a card (`#1c1c26` surface, radius, hover elevation), splitter name shown as a pill/badge, scrubber and volume range inputs restyled with gradient `accent-color`/custom thumb styling to match the new palette.
- **MIDI view**: success checkmark treatment, MIDI download button uses the gradient accent, WAV download stays neutral gray.

## Non-goals

- No changes to job/step/stem data model, API routes, or SSE behavior.
- No new dependencies beyond the Google Fonts `<link>` tags (Alpine.js stays as-is via existing CDN script tag).
- No responsive/mobile-specific redesign beyond what already works with the existing flex layout.
