import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from server import db, pipeline


def test_build_step_labels_no_stretch():
    labels = pipeline._build_step_labels(["demucs", "spleeter"], 1.0)
    assert labels == ["Downloading", "Demucs", "Spleeter"]


def test_build_step_labels_with_stretch():
    labels = pipeline._build_step_labels(["demucs"], 0.5)
    assert labels == ["Downloading", "Time-stretch (0.5x)", "Demucs", "Restore speed"]


def test_time_stretch_skipped_at_1x(tmp_path):
    audio = tmp_path / "input.wav"
    audio.touch()
    result = pipeline._time_stretch(audio, 1.0)
    assert result == audio


def test_time_stretch_calls_ffmpeg_half_speed(tmp_path):
    audio = tmp_path / "input.wav"
    audio.touch()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr=b"")
        result = pipeline._time_stretch(audio, 0.5)
    assert result.name == "input_stretched.wav"
    cmd = " ".join(mock_run.call_args[0][0])
    assert "atempo=0.5" in cmd


def test_time_stretch_025x_chains_two_filters(tmp_path):
    audio = tmp_path / "input.wav"
    audio.touch()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr=b"")
        pipeline._time_stretch(audio, 0.25)
    cmd = " ".join(mock_run.call_args[0][0])
    assert cmd.count("atempo=0.5") == 2


def test_restore_speed_calls_ffmpeg(tmp_path):
    stem = tmp_path / "vocals.wav"
    stem.touch()

    def fake_run(cmd, **kwargs):
        # Simulate ffmpeg creating the restore temp file
        tmp_file = tmp_path / f"_restore_{stem.name}"
        tmp_file.touch()
        return MagicMock(returncode=0, stderr=b"")

    with patch("subprocess.run", side_effect=fake_run) as mock_run:
        pipeline._restore_speed({"vocals": stem}, 0.5)
    cmd = " ".join(mock_run.call_args[0][0])
    assert "atempo=2.0" in cmd


def test_run_job_completed_status():
    job_id = db.create_job("song", "http://yt", ["demucs"], 1.0)

    def fake_download(url, audio_path):
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        audio_path.touch()

    def fake_run_demucs(audio_path, output_dir):
        out = output_dir / "htdemucs" / "input"
        out.mkdir(parents=True, exist_ok=True)
        v = out / "vocals.wav"
        v.touch()
        return {"vocals": v}

    with tempfile.TemporaryDirectory() as base:
        with patch.object(pipeline, "_download", side_effect=fake_download), \
             patch("server.splitters.run_demucs", side_effect=fake_run_demucs):
            pipeline.run_job(job_id, "http://yt", "song", ["demucs"], 1.0, Path(base))

    assert db.get_job(job_id).status == "completed"
    assert any(s.stem_type == "vocals" for s in db.get_stems(job_id))


def test_run_job_partial_failure_still_records_successful_splitters():
    job_id = db.create_job("song", "http://yt", ["demucs", "spleeter"], 1.0)

    def fake_download(url, audio_path):
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        audio_path.touch()

    def fake_demucs(audio_path, output_dir):
        out = output_dir / "htdemucs" / "input"
        out.mkdir(parents=True, exist_ok=True)
        v = out / "vocals.wav"
        v.touch()
        return {"vocals": v}

    def fake_spleeter(audio_path, output_dir):
        raise RuntimeError("spleeter failed")

    with tempfile.TemporaryDirectory() as base:
        with patch.object(pipeline, "_download", side_effect=fake_download), \
             patch("server.splitters.run_demucs", side_effect=fake_demucs), \
             patch("server.splitters.run_spleeter", side_effect=fake_spleeter):
            pipeline.run_job(job_id, "http://yt", "song", ["demucs", "spleeter"], 1.0, Path(base))

    stems = db.get_stems(job_id)
    assert any(s.splitter == "demucs" for s in stems)
    spleeter_step = next(s for s in db.get_steps(job_id) if s.label == "Spleeter")
    assert spleeter_step.status == "failed"
