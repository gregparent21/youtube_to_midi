# server/routes/audio.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from .. import db

router = APIRouter()


@router.get("/audio/stem/{stem_id}")
def serve_stem(stem_id: int):
    stem = db.get_stem(stem_id)
    if not stem:
        raise HTTPException(status_code=404, detail="Stem not found")
    file_path = Path(stem.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found on disk")
    return FileResponse(str(file_path), media_type="audio/wav")


@router.get("/audio/midi/{job_id}")
def serve_midi(job_id: str):
    midi = db.get_midi(job_id)
    if not midi:
        raise HTTPException(status_code=404, detail="MIDI not yet generated")
    path = Path(midi["midi_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="MIDI file not found on disk")
    return FileResponse(str(path), media_type="audio/midi",
                        filename=path.name)
