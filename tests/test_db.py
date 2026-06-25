import pytest
from server import db
from server.models import Job, Step, Stem


def test_create_and_get_job():
    job_id = db.create_job("song", "https://yt.com/v", ["demucs"], 1.0)
    job = db.get_job(job_id)
    assert job.name == "song"
    assert job.url == "https://yt.com/v"
    assert job.splitters == ["demucs"]
    assert job.speed == 1.0
    assert job.status == "pending"


def test_list_jobs():
    db.create_job("a", "url1", ["demucs"], 1.0)
    db.create_job("b", "url2", ["spleeter"], 0.5)
    jobs = db.list_jobs()
    names = [j.name for j in jobs]
    assert "a" in names and "b" in names


def test_update_job_status():
    job_id = db.create_job("s", "url", ["demucs"], 1.0)
    db.update_job_status(job_id, "running")
    assert db.get_job(job_id).status == "running"


def test_steps_lifecycle():
    job_id = db.create_job("s", "url", ["demucs"], 1.0)
    db.create_steps(job_id, ["Downloading", "Demucs"])
    steps = db.get_steps(job_id)
    assert len(steps) == 2
    assert steps[0].label == "Downloading"
    assert steps[0].status == "pending"
    db.update_step(steps[0].id, "completed")
    assert db.get_steps(job_id)[0].status == "completed"


def test_step_error_stored():
    job_id = db.create_job("s", "url", ["demucs"], 1.0)
    db.create_steps(job_id, ["Demucs"])
    step_id = db.get_steps(job_id)[0].id
    db.update_step(step_id, "failed", "stderr output here")
    assert db.get_steps(job_id)[0].error == "stderr output here"


def test_record_and_get_stems():
    job_id = db.create_job("s", "url", ["demucs"], 1.0)
    db.record_stem(job_id, "demucs", "vocals", "/path/vocals.wav")
    stems = db.get_stems(job_id)
    assert len(stems) == 1
    assert stems[0].splitter == "demucs"
    assert stems[0].stem_type == "vocals"
    assert stems[0].file_path == "/path/vocals.wav"


def test_record_and_get_midi():
    job_id = db.create_job("s", "url", ["demucs"], 1.0)
    assert db.get_midi(job_id) is None
    db.record_stem(job_id, "demucs", "vocals", "/path/vocals.wav")
    stem_id = db.get_stems(job_id)[0].id
    db.record_midi(job_id, stem_id, "/path/out.mid", "/path/vocals.wav")
    midi = db.get_midi(job_id)
    assert midi["midi_path"] == "/path/out.mid"
    assert midi["stem_path"] == "/path/vocals.wav"
    assert midi["stem_id"] == stem_id


def test_get_stem_by_id():
    job_id = db.create_job("s", "url", ["demucs"], 1.0)
    db.record_stem(job_id, "demucs", "vocals", "/path/vocals.wav")
    stem_id = db.get_stems(job_id)[0].id
    stem = db.get_stem(stem_id)
    assert stem is not None
    assert stem.stem_type == "vocals"
    assert db.get_stem(99999) is None


def test_get_job_includes_steps_and_stems():
    job_id = db.create_job("s", "url", ["demucs"], 1.0)
    db.create_steps(job_id, ["Downloading"])
    db.record_stem(job_id, "demucs", "vocals", "/path/v.wav")
    job = db.get_job(job_id)
    assert len(job.steps) == 1
    assert len(job.stems) == 1
