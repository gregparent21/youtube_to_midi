# Frontend Design: YouTube to MIDI Web App

**Date:** 2026-06-25
**Status:** Approved

## Overview

A local web app (localhost) that wraps the existing YouTube-to-MIDI pipeline in a browser UI. The user pastes a YouTube URL, selects which stem splitters to run and an optional speed preset, monitors pipeline progress, browses the resulting stems with a synchronized audio player, picks one stem, and downloads the generated MIDI file.

The original `youtube_to_midi.py` CLI remains untouched and fully functional.

---

## Tech Stack

- **Backend:** FastAPI + uvicorn, plain `sqlite3` (no ORM), `threading.Thread` for background jobs
- **Frontend:** Single HTML page, Alpine.js (inlined — no npm, no build step), plain CSS
- **Audio manipulation:** `ffmpeg` `atempo` filter for time-stretch/restore (no pitch change)
- **Stem splitters:** Demucs, Spleeter, audio-separator

---

## Project Structure

```
youtube_to_midi/
├── server/
│   ├── main.py          # FastAPI app, mounts static files, registers routes
│   ├── routes/
│   │   ├── jobs.py      # CRUD + SSE progress endpoint
│   │   └── audio.py     # Serve WAV and MIDI files from disk
│   ├── pipeline.py      # Background job runner (download → stretch → split → restore)
│   ├── splitters.py     # One function per splitter (demucs, spleeter, audio-separator)
│   ├── db.py            # SQLite init and query helpers
│   └── models.py        # Dataclasses: Job, Step, Stem
├── static/
│   ├── index.html       # Single-page app entry point
│   ├── app.js           # Alpine.js component logic
│   └── styles.css
├── youtube_to_midi.py   # Original CLI (unchanged)
└── requirements.txt     # Extended with fastapi, uvicorn, spleeter, audio-separator
```

---

## API Routes

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Serve `index.html` |
| `POST` | `/jobs` | Create job (`url`, `name`, `splitters`, `speed`) |
| `GET` | `/jobs` | List all jobs (sidebar) |
| `GET` | `/jobs/{id}` | Job detail + stems |
| `GET` | `/jobs/{id}/events` | SSE stream — emits step status updates |
| `POST` | `/jobs/{id}/convert` | Run Basic Pitch on chosen stem |
| `GET` | `/audio/{job_id}/{path:path}` | Serve any WAV or MIDI file from disk |

---

## Database Schema (SQLite)

```sql
CREATE TABLE jobs (
  id         TEXT PRIMARY KEY,   -- uuid
  name       TEXT NOT NULL,
  url        TEXT NOT NULL,
  speed      REAL NOT NULL,      -- 0.25 / 0.5 / 0.75 / 1.0
  splitters  TEXT NOT NULL,      -- JSON array e.g. '["demucs","spleeter"]'
  status     TEXT NOT NULL,      -- pending / running / completed / failed
  created_at TEXT NOT NULL
);

CREATE TABLE steps (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id   TEXT NOT NULL,
  label    TEXT NOT NULL,        -- "Downloading", "Demucs", "Spleeter", "Restoring speed"
  status   TEXT NOT NULL,        -- pending / running / completed / failed
  error    TEXT                  -- stderr output on failure, else null
);

CREATE TABLE stems (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id    TEXT NOT NULL,
  splitter  TEXT NOT NULL,       -- demucs / spleeter / audio-separator
  stem_type TEXT NOT NULL,       -- vocals / bass / drums / other
  file_path TEXT NOT NULL        -- absolute path on disk
);
```

---

## Pipeline Execution (`pipeline.py`)

Each job runs in a `threading.Thread`. Steps execute in this order:

1. **Download** — `yt-dlp` extracts audio as `input.wav`
2. **Time-stretch** (skipped if speed = 1.0) — `ffmpeg atempo` slows audio to preset; no pitch shift
3. **Stem separation** — selected splitters run in parallel sub-threads
4. **Restore speed** (skipped if speed = 1.0) — `ffmpeg atempo` restores all stems to 1x

Progress is written to the `steps` table after each state change. The SSE endpoint polls the DB every 500ms and pushes changed rows as JSON events.

**Keep-existing logic:** If a job is re-run with the same name, steps whose output files already exist on disk are marked complete immediately and skipped.

**Splitter availability check:** On server startup, `ensure_command_exists` is called for each splitter. Unavailable splitters are reported via `GET /splitters` so the UI can disable their checkboxes.

---

## Frontend Layout

```
┌─────────────────┬──────────────────────────────────────────┐
│   SIDEBAR       │   MAIN PANEL                             │
│                 │                                          │
│  [+ New Job]    │  INPUT FORM / PROGRESS / STEM BROWSER   │
│                 │                                          │
│  ▸ Song A  ✓   │                                          │
│    Song B  ⟳   │                                          │
│    Song C  ✗   │                                          │
└─────────────────┴──────────────────────────────────────────┘
```

**Main panel views (mutually exclusive, driven by `activeView`):**

- `form` — URL input, name, splitter checkboxes, speed preset radio buttons, Run button
- `progress` — list of pipeline steps with status icons; live-updating via SSE
- `stems` — stem browser (see below) + global scrubber
- `midi` — MIDI download link + stem WAV download link

Clicking any sidebar job restores its view to whatever stage it is at (`progress` if still running, `stems` if complete and no MIDI yet, `midi` if conversion done, `form` if failed before producing stems).

---

## Alpine.js State

Single `x-data` object on `<body>`:

```js
{
  // sidebar
  jobs: [],
  activeJobId: null,
  activeView: 'form',       // 'form' | 'progress' | 'stems' | 'midi'

  // progress
  steps: [],

  // stem browser
  stems: {},                // { vocals: [{splitter, filePath}, ...], bass: [...], ... }
  selectedStem: null,       // { splitter, stemType, filePath }

  // global synchronized playhead
  playhead: 0,              // seconds — shared across all audio elements
  duration: 0,              // set from whichever stem loads first
  activeStemKey: null,      // currently-playing "splitter:stemType" key

  // midi
  midiPath: null,
  stemWavPath: null,
  converting: false,
}
```

---

## Synchronized Playhead

There is **one scrubber bar** pinned to the bottom of the stem browser. Per-stem rows show only a play/pause button and elapsed time text — no individual scrubbers.

**Sync rules:**
- `@timeupdate` on any `<audio>` element → writes `playhead`
- Scrubber `input` event → writes `playhead` → calls `.currentTime = playhead` on all other loaded audio elements
- Clicking play on any stem → seeks that element to `playhead` before playing, pauses all others
- When switching to a different stem, the new element seeks to `playhead` immediately

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Subprocess exits non-zero | Step marked `failed`, stderr stored in `steps.error`, SSE pushes failure, UI shows red step with expandable error text |
| One splitter fails, others succeed | Only that splitter's step fails; stem browser shows successful splitters only |
| Splitter not installed | Checkbox disabled in UI with tooltip on page load |
| Audio file missing from disk | `/audio/` returns 404; frontend renders "file missing" placeholder |
| SSE connection drops | On reconnect, `GET /jobs/{id}` fetches current snapshot; SSE stream re-opened |
| Job name collision | Server appends numeric suffix (`song-2`, `song-3`, etc.) |

---

## Future Extension Point

The MIDI conversion step is designed as a discrete view (`midi`) with its own route (`POST /jobs/{id}/convert`). A future "Send to piano visualizer" button can be added to the `midi` view without touching the rest of the pipeline.

---

## Out of Scope

- Spotify support (deferred)
- Deployed/hosted version (local only)
- Live waveform visualization
- MIDI playback in the browser
