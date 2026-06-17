#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path


STEMS = ["vocals", "drums", "bass", "other"]


def run(cmd, cwd=None):
    print(f"\n▶ Running: {' '.join(map(str, cmd))}\n")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Command failed: {' '.join(map(str, cmd))}")
        sys.exit(result.returncode)


def ensure_command_exists(command):
    result = subprocess.run(
        ["which", command],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        print(f"❌ Missing command: {command}")
        print(f"Install it first, then rerun this script.")
        sys.exit(1)


def find_demucs_output(work_dir, song_stem):
    separated_dir = work_dir / "separated"

    if not separated_dir.exists():
        print("❌ Could not find Demucs output folder.")
        sys.exit(1)

    possible_dirs = list(separated_dir.glob(f"*/{song_stem}"))

    if not possible_dirs:
        print("❌ Could not find separated stems.")
        print(f"Looked inside: {separated_dir}")
        sys.exit(1)

    return possible_dirs[0]


def choose_stem(stems_dir):
    available = []

    for stem in STEMS:
        path = stems_dir / f"{stem}.wav"
        if path.exists():
            available.append(stem)

    if not available:
        print("❌ No stem files found.")
        sys.exit(1)

    print("\nAvailable stems:")
    for i, stem in enumerate(available, start=1):
        print(f"{i}. {stem}")

    while True:
        choice = input("\nChoose a stem number to convert to MIDI: ").strip()

        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(available):
                return available[index]

        print("Invalid choice. Try again.")


def main():
    parser = argparse.ArgumentParser(
        description="Download audio from a YouTube URL, split it with Demucs, choose a stem, and convert it to MIDI with Basic Pitch."
    )

    parser.add_argument("url", help="YouTube URL")
    parser.add_argument(
        "--name",
        default="song",
        help="Name for the working folder and downloaded audio file. Default: song",
    )
    parser.add_argument(
        "--stem",
        choices=STEMS,
        help="Stem to convert directly: vocals, drums, bass, or other. If omitted, you will be prompted.",
    )
    parser.add_argument(
        "--model-serialization",
        default="coreml",
        choices=["coreml", "tensorflow", "tflite", "onnx"],
        help="Basic Pitch model backend. Default: coreml",
    )
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Skip steps when existing files are found.",
    )

    args = parser.parse_args()

    ensure_command_exists("yt-dlp")
    ensure_command_exists("demucs")
    ensure_command_exists("basic-pitch")
    ensure_command_exists("ffmpeg")

    base_dir = Path.cwd()
    work_dir = base_dir / args.name
    work_dir.mkdir(exist_ok=True)

    audio_path = work_dir / "input.wav"
    midi_dir = work_dir / "midi_output"
    midi_dir.mkdir(exist_ok=True)

    # 1. Download YouTube audio as WAV
    if audio_path.exists() and args.keep_existing:
        print(f"✅ Using existing audio file: {audio_path}")
    else:
        run(
            [
                "yt-dlp",
                "-x",
                "--audio-format",
                "wav",
                "-o",
                str(work_dir / "input.%(ext)s"),
                args.url,
            ]
        )

    if not audio_path.exists():
        print(f"❌ Expected audio file not found: {audio_path}")
        sys.exit(1)

    # 2. Split into stems with Demucs
    stems_dir = find_demucs_output(work_dir, "input") if args.keep_existing else None

    if stems_dir and args.keep_existing:
        print(f"✅ Using existing Demucs stems: {stems_dir}")
    else:
        run(
            [
                "demucs",
                "-o",
                str(work_dir / "separated"),
                str(audio_path),
            ]
        )
        stems_dir = find_demucs_output(work_dir, "input")

    print(f"\n✅ Demucs stems created at:\n{stems_dir}")

    for stem in STEMS:
        stem_path = stems_dir / f"{stem}.wav"
        if stem_path.exists():
            print(f"  - {stem_path}")

    # 3. Select stem
    selected_stem = args.stem if args.stem else choose_stem(stems_dir)
    selected_audio = stems_dir / f"{selected_stem}.wav"

    if not selected_audio.exists():
        print(f"❌ Stem not found: {selected_audio}")
        sys.exit(1)

    print(f"\n🎵 Selected stem: {selected_stem}")
    print(f"Audio file: {selected_audio}")

    # 4. Convert selected stem to MIDI with Basic Pitch
    run(
        [
            "basic-pitch",
            "--model-serialization",
            args.model_serialization,
            str(midi_dir),
            str(selected_audio),
        ]
    )

    print("\n✅ Done.")
    print(f"Stems folder: {stems_dir}")
    print(f"MIDI output folder: {midi_dir}")

    midi_files = list(midi_dir.glob("*.mid"))
    if midi_files:
        print("\nGenerated MIDI files:")
        for midi in midi_files:
            print(f"  - {midi}")
    else:
        print("\n⚠️ No .mid file found, but Basic Pitch finished. Check the MIDI output folder.")


if __name__ == "__main__":
    main()