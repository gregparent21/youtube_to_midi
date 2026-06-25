# server/pipeline.py
import subprocess
import threading
from pathlib import Path

from . import db, splitters

# (slow_filters, restore_filters) for each speed preset
SPEED_FILTERS = {
    0.25: (["atempo=0.5", "atempo=0.5"], ["atempo=2.0", "atempo=2.0"]),
    0.5:  (["atempo=0.5"],               ["atempo=2.0"]),
    0.75: (["atempo=0.75"],              ["atempo=1.333333"]),
    1.0:  ([],                           []),
}

_SPLITTER_METHOD_NAMES = {
    "demucs":          "run_demucs",
    "spleeter":        "run_spleeter",
    "audio-separator": "run_audio_separator",
}


def _build_step_labels(splitters_list, speed):
    labels = ["Downloading"]
    if speed != 1.0:
        labels.append(f"Time-stretch ({speed}x)")
    labels.extend(splitters.SPLITTER_LABELS[s] for s in splitters_list)
    if speed != 1.0:
        labels.append("Restore speed")
    return labels


def _run_subprocess(cmd):
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace"))


def _download(url, audio_path):
    _run_subprocess([
        "yt-dlp", "-x", "--audio-format", "wav",
        "-o", str(audio_path.parent / "input.%(ext)s"),
        url,
    ])


def _time_stretch(audio_path: Path, speed: float) -> Path:
    if speed == 1.0:
        return audio_path
    slow_filters, _ = SPEED_FILTERS[speed]
    out_path = audio_path.parent / f"{audio_path.stem}_stretched.wav"
    _run_subprocess([
        "ffmpeg", "-y", "-i", str(audio_path),
        "-filter:a", ",".join(slow_filters),
        str(out_path),
    ])
    return out_path


def _restore_speed(stems: dict, speed: float):
    if speed == 1.0:
        return
    _, restore_filters = SPEED_FILTERS[speed]
    filter_str = ",".join(restore_filters)
    for stem_path in stems.values():
        tmp = stem_path.parent / f"_restore_{stem_path.name}"
        _run_subprocess([
            "ffmpeg", "-y", "-i", str(stem_path),
            "-filter:a", filter_str,
            str(tmp),
        ])
        if tmp.exists():
            tmp.replace(stem_path)


def run_job(job_id, url, name, splitters_list, speed, base_dir: Path):
    work_dir = base_dir / name
    work_dir.mkdir(exist_ok=True)
    audio_path = work_dir / "input.wav"

    labels = _build_step_labels(splitters_list, speed)
    db.create_steps(job_id, labels)
    db.update_job_status(job_id, "running")

    steps = db.get_steps(job_id)
    step_map = {s.label: s.id for s in steps}

    def mark(label, status, error=None):
        db.update_step(step_map[label], status, error)

    try:
        mark("Downloading", "running")
        _download(url, audio_path)
        mark("Downloading", "completed")

        active_audio = audio_path
        if speed != 1.0:
            stretch_label = f"Time-stretch ({speed}x)"
            mark(stretch_label, "running")
            active_audio = _time_stretch(audio_path, speed)
            mark(stretch_label, "completed")

        splitter_results = {}
        errors = {}
        lock = threading.Lock()

        def run_one(splitter_name):
            label = splitters.SPLITTER_LABELS[splitter_name]
            mark(label, "running")
            out_dir = work_dir / "separated" / splitter_name
            out_dir.mkdir(parents=True, exist_ok=True)
            runner = getattr(splitters, _SPLITTER_METHOD_NAMES[splitter_name])
            try:
                stems = runner(active_audio, out_dir)
                with lock:
                    splitter_results[splitter_name] = stems
                mark(label, "completed")
            except Exception as exc:
                with lock:
                    errors[splitter_name] = str(exc)
                mark(label, "failed", str(exc))

        threads = [threading.Thread(target=run_one, args=(s,)) for s in splitters_list]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        if speed != 1.0:
            mark("Restore speed", "running")
            for stems in splitter_results.values():
                _restore_speed(stems, speed)
            mark("Restore speed", "completed")

        for splitter_name, stems in splitter_results.items():
            for stem_type, file_path in stems.items():
                db.record_stem(job_id, splitter_name, stem_type, str(file_path))

        final_status = "completed" if splitter_results else "failed"
        db.update_job_status(job_id, final_status)

    except Exception as exc:
        db.update_job_status(job_id, "failed")
        raise
