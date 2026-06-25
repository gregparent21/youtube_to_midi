# server/main.py
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routes.audio import router as audio_router
from .routes.jobs import router as jobs_router

app = FastAPI(title="YouTube to MIDI")
BASE_DIR = Path(__file__).parent.parent


@app.on_event("startup")
def startup():
    init_db()


app.include_router(jobs_router)
app.include_router(audio_router)

_static = BASE_DIR / "static"
if _static.exists():
    app.mount("/static", StaticFiles(directory=_static), name="static")


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")
