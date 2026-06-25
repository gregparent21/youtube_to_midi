import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from server import db as db_module
from server.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_audio_stem_serves_wav(client, tmp_path):
    wav = tmp_path / "vocals.wav"
    wav.write_bytes(b"RIFF" + b"\x00" * 40)
    job_id = db_module.create_job("s", "url", ["demucs"], 1.0)
    db_module.record_stem(job_id, "demucs", "vocals", str(wav))
    stem_id = db_module.get_stems(job_id)[0].id

    resp = client.get(f"/audio/stem/{stem_id}")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("audio/")


def test_audio_stem_404_missing_file(client, tmp_path):
    job_id = db_module.create_job("s", "url", ["demucs"], 1.0)
    db_module.record_stem(job_id, "demucs", "vocals", str(tmp_path / "missing.wav"))
    stem_id = db_module.get_stems(job_id)[0].id

    resp = client.get(f"/audio/stem/{stem_id}")
    assert resp.status_code == 404


def test_audio_midi_404_before_conversion(client):
    job_id = db_module.create_job("s", "url", ["demucs"], 1.0)
    resp = client.get(f"/audio/midi/{job_id}")
    assert resp.status_code == 404


def test_convert_endpoint_runs_basic_pitch(client, tmp_path):
    wav = tmp_path / "vocals.wav"
    wav.write_bytes(b"RIFF" + b"\x00" * 40)

    job_id = db_module.create_job("s", "url", ["demucs"], 1.0)
    db_module.record_stem(job_id, "demucs", "vocals", str(wav))
    stem_id = db_module.get_stems(job_id)[0].id

    def fake_run(cmd, **kwargs):
        # basic-pitch writes to the output dir (cmd[-2]); create a fake .mid there
        out_dir = Path(cmd[-2])
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "vocals_basic_pitch.mid").touch()
        return MagicMock(returncode=0, stderr=b"")

    with patch("subprocess.run", side_effect=fake_run):
        resp = client.post(f"/jobs/{job_id}/convert", json={"stem_id": stem_id})

    assert resp.status_code == 200
    data = resp.json()
    assert "midi_path" in data
    assert data["stem_id"] == stem_id


def test_sse_emits_done_for_completed_job(client):
    job_id = db_module.create_job("s", "url", ["demucs"], 1.0)
    db_module.create_steps(job_id, ["Downloading"])
    step_id = db_module.get_steps(job_id)[0].id
    db_module.update_step(step_id, "completed")
    db_module.update_job_status(job_id, "completed")

    with client.stream("GET", f"/jobs/{job_id}/events") as resp:
        assert resp.status_code == 200
        events = []
        for line in resp.iter_lines():
            if line.startswith("data:"):
                events.append(json.loads(line[5:].strip()))
            if any(e.get("type") == "done" for e in events):
                break

    assert any(e["type"] == "done" for e in events)
