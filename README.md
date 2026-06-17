# YouTube Audio to MIDI Pipeline

This project takes a YouTube video URL, downloads the audio, separates the song into individual stems using Demucs, and converts one selected stem into a MIDI file using Basic Pitch.

## Flow

1. **Download audio from YouTube**
   - Uses `yt-dlp` to extract the audio from a YouTube URL.
   - Saves the audio as `input.wav`.

2. **Separate audio into stems**
   - Uses `Demucs` to split the audio into:
     - `vocals.wav`
     - `drums.wav`
     - `bass.wav`
     - `other.wav`

3. **Select a stem**
   - The script lets you choose which stem to convert.
   - For cleaner MIDI, `vocals.wav` or `bass.wav` usually works better than `other.wav`.

4. **Convert stem to MIDI**
   - Uses `Basic Pitch` to convert the selected `.wav` stem into a `.mid` file.
   - The MIDI output is saved in the `midi_output/` folder.

## Setup

Create and activate a Python environment:

```bash
conda create -n basicpitch python=3.10 pip -y
conda activate basicpitch
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install `ffmpeg` separately:

```bash
brew install ffmpeg
```

## Usage

Run the script from the project directory:

```bash
python youtube_to_midi.py "YOUTUBE_URL" --name song_name
```

Example:

```bash
python youtube_to_midi.py "https://www.youtube.com/watch?v=example" --name song_name
```

To skip the interactive selection and choose a stem directly:

```bash
python youtube_to_midi.py "YOUTUBE_URL" --name song_name --stem vocals
```

Other stem options:

```bash
--stem vocals
--stem bass
--stem drums
--stem other
```

## Output Structure

After running, the project creates a folder like:

```text
song_name/
  input.wav
  separated/
    htdemucs/
      input/
        vocals.wav
        drums.wav
        bass.wav
        other.wav
  midi_output/
    selected_stem_basic_pitch.mid
```

## Notes

MIDI conversion works best on isolated, simple stems. Full mixes or the `other.wav` stem may produce noisy results because they often contain multiple instruments at once. After generating the MIDI, it is usually worth cleaning it up in a DAW like GarageBand, Logic, Ableton, FL Studio, Reaper, or MuseScore.
