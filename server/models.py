# server/models.py
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Step:
    id: int
    job_id: str
    label: str
    status: str
    error: Optional[str] = None


@dataclass
class Stem:
    id: int
    job_id: str
    splitter: str
    stem_type: str
    file_path: str


@dataclass
class Job:
    id: str
    name: str
    url: str
    speed: float
    splitters: list
    status: str
    created_at: str
    steps: list = field(default_factory=list)
    stems: list = field(default_factory=list)
