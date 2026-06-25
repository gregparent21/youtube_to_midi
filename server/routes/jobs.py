# server/routes/jobs.py
import shutil
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import db

router = APIRouter()

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
    job_id = db.create_job(body.name, body.url, body.splitters, body.speed)
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
