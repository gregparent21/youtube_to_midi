# server/routes/jobs.py
import asyncio
import json as json_lib
import shutil
import subprocess
import threading
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from .. import db
from ..pipeline import run_job, _get_base_dir

router = APIRouter()

BASE_DIR = Path(__file__).parent.parent.parent

SPLITTER_DEFS = [
    {"name": "demucs",          "label": "Demucs"},
    {"name": "spleeter",        "label": "Spleeter"},
    {"name": "audio-separator", "label": "audio-separator"},
]


class JobCreate(BaseModel):
    url: str
    name: str
    splitters: list
    speed: float = 1.0


@router.get("/splitters")
def get_splitters():
    return [
        {**s, "available": shutil.which(s["name"]) is not None}
        for s in SPLITTER_DEFS
    ]


@router.post("/jobs", status_code=201)
def create_job(body: JobCreate):
    final_name = body.name
    counter = 2
    while (_get_base_dir(BASE_DIR) / final_name).exists():
        final_name = f"{body.name}-{counter}"
        counter += 1

    job_id = db.create_job(final_name, body.url, body.splitters, body.speed)

    t = threading.Thread(
        target=run_job,
        args=(job_id, body.url, final_name, body.splitters, body.speed, _get_base_dir(BASE_DIR)),
        daemon=True,
    )
    t.start()

    job = db.get_job(job_id)
    return {
        **job.__dict__,
        "steps": [s.__dict__ for s in job.steps],
        "stems": [s.__dict__ for s in job.stems],
    }


@router.get("/jobs")
def list_jobs():
    return [
        {**j.__dict__, "steps": [], "stems": []}
        for j in db.list_jobs()
    ]


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        **job.__dict__,
        "steps": [s.__dict__ for s in job.steps],
        "stems": [s.__dict__ for s in job.stems],
        "midi": db.get_midi(job_id),
    }


@router.get("/jobs/{job_id}/events")
async def job_events(job_id: str):
    if not db.get_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")

    async def generate():
        seen = {}
        while True:
            steps = db.get_steps(job_id)
            job = db.get_job(job_id)
            for step in steps:
                if seen.get(step.id) != step.status:
                    seen[step.id] = step.status
                    yield {
                        "data": json_lib.dumps({
                            "type": "step",
                            "id": step.id,
                            "label": step.label,
                            "status": step.status,
                            "error": step.error,
                        })
                    }
            if job and job.status in ("completed", "failed"):
                yield {"data": json_lib.dumps({"type": "done", "status": job.status})}
                return
            await asyncio.sleep(0.5)

    return EventSourceResponse(generate())


class ConvertRequest(BaseModel):
    stem_id: int


@router.post("/jobs/{job_id}/convert")
def convert_to_midi(job_id: str, body: ConvertRequest):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    stems = db.get_stems(job_id)
    stem = next((s for s in stems if s.id == body.stem_id), None)
    if not stem:
        raise HTTPException(status_code=404, detail="Stem not found")

    stem_path = Path(stem.file_path)
    midi_dir = stem_path.parent.parent.parent / "midi_output"
    midi_dir.mkdir(exist_ok=True)

    result = subprocess.run(
        ["basic-pitch", str(midi_dir), str(stem_path)],
        capture_output=True,
    )
    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=result.stderr.decode(errors="replace"),
        )

    stem_name = Path(stem.file_path).stem
    midi_files = list(midi_dir.glob(f"{stem_name}_basic_pitch.mid"))
    if not midi_files:
        # Fall back to any .mid if the naming convention changed
        midi_files = list(midi_dir.glob("*.mid"))
    if not midi_files:
        raise HTTPException(
            status_code=500,
            detail="basic-pitch ran but produced no .mid file"
        )

    midi_path = str(midi_files[0])
    db.record_midi(job_id, body.stem_id, midi_path, stem.file_path)
    return {"midi_path": midi_path, "stem_path": stem.file_path, "stem_id": body.stem_id}
