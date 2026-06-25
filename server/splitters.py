# server/splitters.py
import shutil
import subprocess
from pathlib import Path

STEM_TYPES = ["vocals", "drums", "bass", "other"]

SPLITTER_LABELS = {
    "demucs":          "Demucs",
    "spleeter":        "Spleeter",
    "audio-separator": "audio-separator",
}


def check_available():
    return {name: shutil.which(name) is not None for name in SPLITTER_LABELS}


def _run(cmd):
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace"))


def run_demucs(audio_path: Path, output_dir: Path) -> dict:
    _run(["demucs", "-o", str(output_dir), str(audio_path)])
    # Demucs nests output under model name: output_dir/{model}/{audio_stem}/
    candidates = list(output_dir.glob(f"*/{audio_path.stem}"))
    if not candidates:
        raise RuntimeError(f"demucs output not found under {output_dir}")
    stems_dir = candidates[0]
    return {
        stem: stems_dir / f"{stem}.wav"
        for stem in STEM_TYPES
        if (stems_dir / f"{stem}.wav").exists()
    }


def run_spleeter(audio_path: Path, output_dir: Path) -> dict:
    _run(["spleeter", "separate", "-p", "spleeter:4stems",
          "-o", str(output_dir), str(audio_path)])
    # Spleeter outputs to output_dir/{audio_stem}/
    stems_dir = output_dir / audio_path.stem
    return {
        stem: stems_dir / f"{stem}.wav"
        for stem in STEM_TYPES
        if (stems_dir / f"{stem}.wav").exists()
    }


def run_audio_separator(audio_path: Path, output_dir: Path) -> dict:
    _run(["audio-separator", str(audio_path), "--output_dir", str(output_dir)])
    # Default model produces 2-stem: (Vocals) and (No Vocals)
    result = {}
    for f in output_dir.glob(f"{audio_path.stem}_*(Vocals)*.wav"):
        if "(No Vocals)" not in f.name:
            result["vocals"] = f
    for f in output_dir.glob(f"{audio_path.stem}_*(No Vocals)*.wav"):
        result["other"] = f
    if not result:
        raise RuntimeError(f"audio-separator output not found under {output_dir}")
    return result
