# server/db.py
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .models import Job, Step, Stem

_DEFAULT_DB_PATH = Path(__file__).parent.parent / "jobs.db"
_db_path = None


def set_db_path(path):
    global _db_path
    _db_path = Path(path) if path else None


def _get_path():
    return _db_path or _DEFAULT_DB_PATH


@contextmanager
def _conn():
    conn = sqlite3.connect(_get_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id         TEXT PRIMARY KEY,
                name       TEXT NOT NULL,
                url        TEXT NOT NULL,
                speed      REAL NOT NULL,
                splitters  TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id   TEXT NOT NULL,
                label    TEXT NOT NULL,
                status   TEXT NOT NULL DEFAULT 'pending',
                error    TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stems (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id    TEXT NOT NULL,
                splitter  TEXT NOT NULL,
                stem_type TEXT NOT NULL,
                file_path TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS midi_outputs (
                job_id    TEXT PRIMARY KEY,
                stem_id   INTEGER NOT NULL,
                midi_path TEXT NOT NULL,
                stem_path TEXT NOT NULL
            )
        """)


def _row_to_job(row, steps=None, stems=None):
    return Job(
        id=row["id"],
        name=row["name"],
        url=row["url"],
        speed=row["speed"],
        splitters=json.loads(row["splitters"]),
        status=row["status"],
        created_at=row["created_at"],
        steps=steps or [],
        stems=stems or [],
    )


def create_job(name, url, splitters, speed):
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO jobs (id, name, url, speed, splitters, status, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (job_id, name, url, speed, json.dumps(splitters), "pending", now),
        )
    return job_id


def get_job(job_id):
    with _conn() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            return None
        steps = [
            Step(id=r["id"], job_id=r["job_id"], label=r["label"],
                 status=r["status"], error=r["error"])
            for r in conn.execute(
                "SELECT * FROM steps WHERE job_id=? ORDER BY id", (job_id,)
            )
        ]
        stems = [
            Stem(id=r["id"], job_id=r["job_id"], splitter=r["splitter"],
                 stem_type=r["stem_type"], file_path=r["file_path"])
            for r in conn.execute("SELECT * FROM stems WHERE job_id=? ORDER BY id", (job_id,))
        ]
        return _row_to_job(row, steps, stems)


def list_jobs():
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC"
        ).fetchall()
        return [_row_to_job(r) for r in rows]


def update_job_status(job_id, status):
    with _conn() as conn:
        conn.execute("UPDATE jobs SET status=? WHERE id=?", (status, job_id))


def create_steps(job_id, labels):
    with _conn() as conn:
        conn.executemany(
            "INSERT INTO steps (job_id, label, status) VALUES (?, ?, 'pending')",
            [(job_id, label) for label in labels],
        )


def update_step(step_id, status, error=None):
    with _conn() as conn:
        conn.execute(
            "UPDATE steps SET status=?, error=? WHERE id=?",
            (status, error, step_id),
        )


def get_steps(job_id):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM steps WHERE job_id=? ORDER BY id", (job_id,)
        ).fetchall()
        return [
            Step(id=r["id"], job_id=r["job_id"], label=r["label"],
                 status=r["status"], error=r["error"])
            for r in rows
        ]


def record_stem(job_id, splitter, stem_type, file_path):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO stems (job_id, splitter, stem_type, file_path) VALUES (?,?,?,?)",
            (job_id, splitter, stem_type, str(file_path)),
        )


def get_stems(job_id):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM stems WHERE job_id=? ORDER BY id", (job_id,)
        ).fetchall()
        return [
            Stem(id=r["id"], job_id=r["job_id"], splitter=r["splitter"],
                 stem_type=r["stem_type"], file_path=r["file_path"])
            for r in rows
        ]


def get_stem(stem_id):
    with _conn() as conn:
        row = conn.execute("SELECT * FROM stems WHERE id=?", (stem_id,)).fetchone()
        if not row:
            return None
        return Stem(id=row["id"], job_id=row["job_id"], splitter=row["splitter"],
                    stem_type=row["stem_type"], file_path=row["file_path"])


def record_midi(job_id, stem_id, midi_path, stem_path):
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO midi_outputs (job_id, stem_id, midi_path, stem_path) "
            "VALUES (?,?,?,?)",
            (job_id, stem_id, str(midi_path), str(stem_path)),
        )


def get_midi(job_id):
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM midi_outputs WHERE job_id=?", (job_id,)
        ).fetchone()
        if not row:
            return None
        return {"stem_id": row["stem_id"], "midi_path": row["midi_path"],
                "stem_path": row["stem_path"]}
