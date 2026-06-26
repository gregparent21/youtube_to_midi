// static/app.js

// Alpine Store: global audio player state shared across all stem rows
document.addEventListener('alpine:init', () => {
  Alpine.store('player', {
    playhead: 0,
    duration: 0,
    volume: 1,
    activeStemKey: null,
    paused: true,
    _elements: {},

    register(key, el) {
      this._elements[key] = el;
    },

    unregisterAll() {
      this._elements = {};
      this.playhead = 0;
      this.duration = 0;
      this.activeStemKey = null;
      this.paused = true;
    },

    onTimeUpdate(key, time) {
      if (key === this.activeStemKey) {
        this.playhead = time;
      }
    },

    onMetadata(dur) {
      if (!this.duration) this.duration = dur;
    },

    toggle(key) {
      const el = this._elements[key];
      if (!el) return;
      if (this.activeStemKey === key && !this.paused) {
        el.pause();
        this.paused = true;
      } else {
        if (this.activeStemKey && this._elements[this.activeStemKey]) {
          this._elements[this.activeStemKey].pause();
        }
        this.activeStemKey = key;
        el.currentTime = this.playhead;
        el.play();
        this.paused = false;
      }
    },

    seek(time) {
      this.playhead = parseFloat(time);
      Object.values(this._elements).forEach(el => {
        el.currentTime = this.playhead;
      });
    },

    setVolume(v) {
      this.volume = parseFloat(v);
      Object.values(this._elements).forEach(el => {
        el.volume = this.volume;
      });
    },

    formatTime(s) {
      const m = Math.floor(s / 60);
      const sec = Math.floor(s % 60).toString().padStart(2, '0');
      return `${m}:${sec}`;
    }
  });
});

function appRoot() {
  return {
    // Sidebar
    jobs: [],
    activeJobId: null,
    activeView: 'form',  // 'form' | 'progress' | 'stems' | 'midi'

    // Available splitters from server
    availableSplitters: [],

    // Form
    form: { url: '', name: '', splitters: [], speed: 1.0 },

    // Progress
    steps: [],
    _evtSource: null,

    // Stem browser — { vocals: [{id, splitter, stemType, fileUrl}, ...], ... }
    stems: {},

    // MIDI
    midiInfo: null,
    converting: false,
    convertError: null,

    async init() {
      const splRes = await fetch('/splitters');
      this.availableSplitters = await splRes.json();
      this.form.splitters = this.availableSplitters
        .filter(s => s.available)
        .map(s => s.name);
      await this.loadJobs();
    },

    async loadJobs() {
      const res = await fetch('/jobs');
      this.jobs = await res.json();
    },

    statusIcon(status) {
      return { pending: '○', running: '⟳', completed: '✓', failed: '✗' }[status] || '?';
    },

    async selectJob(job) {
      this.activeJobId = job.id;
      const res = await fetch(`/jobs/${job.id}`);
      const data = await res.json();

      this.midiInfo = null;
      this.convertError = null;
      this.steps = data.steps || [];

      // Determine which view to show
      if (data.midi) {
        this.midiInfo = { jobId: job.id, stemId: data.midi.stem_id };
        this.activeView = 'midi';
        return;
      }

      if (data.status === 'completed' && data.stems.length > 0) {
        this._populateStems(data.stems);
        this.activeView = 'stems';
      } else if (['running', 'pending'].includes(data.status)) {
        this.activeView = 'progress';
        this._startSSE(job.id);
      } else {
        this.activeView = data.stems.length > 0 ? 'stems' : 'form';
      }
    },

    newJob() {
      this.activeJobId = null;
      this.activeView = 'form';
      this.convertError = null;
      if (this._evtSource) { this._evtSource.close(); this._evtSource = null; }
    },

    _populateStems(stemsArray) {
      Alpine.store('player').unregisterAll();
      const grouped = {};
      for (const stem of stemsArray) {
        if (!grouped[stem.stem_type]) grouped[stem.stem_type] = [];
        grouped[stem.stem_type].push({
          id: stem.id,
          splitter: stem.splitter,
          stemType: stem.stem_type,
          fileUrl: `/audio/stem/${stem.id}`,
        });
      }
      this.stems = grouped;
    },

    _startSSE(jobId) {
      if (this._evtSource) this._evtSource.close();
      this._evtSource = new EventSource(`/jobs/${jobId}/events`);
      this._evtSource.onmessage = (e) => {
        const event = JSON.parse(e.data);
        if (event.type === 'step') {
          const idx = this.steps.findIndex(s => s.id === event.id);
          if (idx >= 0) {
            this.steps[idx] = { ...this.steps[idx], ...event };
          } else {
            this.steps.push(event);
          }
        } else if (event.type === 'done') {
          this._evtSource.close();
          this._evtSource = null;
          this.loadJobs();
          if (event.status === 'completed') {
            fetch(`/jobs/${jobId}`).then(r => r.json()).then(data => {
              this._populateStems(data.stems);
              this.activeView = 'stems';
            });
          }
        }
      };
    },

    async submitJob() {
      if (!this.form.url || !this.form.name || this.form.splitters.length === 0) return;
      const res = await fetch('/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.form),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
        this.convertError = err.detail || 'Failed to start job';
        return;
      }
      const job = await res.json();
      await this.loadJobs();
      this.activeJobId = job.id;
      this.steps = job.steps || [];
      this.activeView = 'progress';
      this._startSSE(job.id);
    },

    async convertToMidi(stemId) {
      this.converting = true;
      this.convertError = null;
      const res = await fetch(`/jobs/${this.activeJobId}/convert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stem_id: stemId }),
      });
      this.converting = false;
      if (!res.ok) {
        this.convertError = (await res.json()).detail || 'Conversion failed';
        return;
      }
      this.midiInfo = { jobId: this.activeJobId, stemId };
      this.activeView = 'midi';
      await this.loadJobs();
    },

    stepIcon(status) {
      return { pending: '○', running: '⟳', completed: '✓', failed: '✗' }[status] || '?';
    },

    stemOrder: ['vocals', 'bass', 'drums', 'other'],

    orderedStemTypes() {
      return this.stemOrder.filter(t => this.stems[t] && this.stems[t].length > 0);
    },
  };
}
