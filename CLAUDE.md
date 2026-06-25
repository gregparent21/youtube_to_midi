# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

Single-script Python CLI that chains three external ML tools to convert YouTube audio into MIDI:

1. `yt-dlp` — downloads audio as `input.wav`
2. `demucs` — separates into 4 stems (vocals, drums, bass, other)
3. `basic-pitch` — converts one selected stem to `.mid`

MIDI quality is better on isolated stems (vocals, bass) than on full mixes.

## Setup

```bash
conda create -n basicpitch python=3.10 pip -y
conda activate basicpitch
pip install -r requirements.txt
# ffmpeg must be installed separately (e.g. brew install ffmpeg on macOS)
```

## Running

```bash
python youtube_to_midi.py "YOUTUBE_URL" --name song_name
python youtube_to_midi.py "YOUTUBE_URL" --name song_name --stem vocals   # skip interactive prompt
python youtube_to_midi.py "YOUTUBE_URL" --name song_name --keep-existing  # resume, reuse existing files
```

`--model-serialization` controls the Basic Pitch backend (default: `coreml`; options: `tensorflow`, `tflite`, `onnx`). Use a non-coreml backend on non-Apple hardware.

## Output Layout

```
<name>/
  input.wav
  separated/htdemucs/input/
    vocals.wav  drums.wav  bass.wav  other.wav
  midi_output/
    <stem>_basic_pitch.mid
```

## Architecture

Everything lives in `youtube_to_midi.py`. The pipeline is strictly linear — each step writes files that the next step reads. `--keep-existing` skips a step when its output files are already present on disk, which is useful when iterating on MIDI conversion without re-downloading or re-separating.

`find_demucs_output()` globs for the stems directory because Demucs nests output under a model-name subdirectory (`htdemucs/` by default) that can change across versions.

There are no tests and no build step.
