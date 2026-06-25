import pytest
from fastapi.testclient import TestClient
from server.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_create_job(client):
    resp = client.post("/jobs", json={
        "url": "https://youtube.com/watch?v=abc",
        "name": "mysong",
        "splitters": ["demucs"],
        "speed": 1.0,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "mysong"
    assert data["status"] == "pending"
    assert "id" in data


def test_list_jobs(client):
    client.post("/jobs", json={"url": "u1", "name": "a", "splitters": ["demucs"], "speed": 1.0})
    client.post("/jobs", json={"url": "u2", "name": "b", "splitters": ["demucs"], "speed": 0.5})
    resp = client.get("/jobs")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


def test_get_job(client):
    create = client.post("/jobs", json={"url": "u", "name": "s", "splitters": ["demucs"], "speed": 1.0})
    job_id = create.json()["id"]
    resp = client.get(f"/jobs/{job_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == job_id
    assert "steps" in resp.json()
    assert "stems" in resp.json()


def test_get_job_404(client):
    resp = client.get("/jobs/nonexistent-id")
    assert resp.status_code == 404


def test_get_splitters(client):
    resp = client.get("/splitters")
    assert resp.status_code == 200
    data = resp.json()
    names = [s["name"] for s in data]
    assert "demucs" in names
    assert "spleeter" in names
    assert "audio-separator" in names
    for s in data:
        assert "available" in s
        assert isinstance(s["available"], bool)
