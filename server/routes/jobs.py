# server/routes/jobs.py
import shutil
import threading
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
