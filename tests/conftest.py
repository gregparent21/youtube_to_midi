# tests/conftest.py
import pytest
import server.db as db_module
import server.pipeline as pipeline_module


@pytest.fixture(autouse=True)
def isolate_db(tmp_path):
    db_module.set_db_path(tmp_path / "test.db")
    db_module.init_db()
    yield
    db_module.set_db_path(None)


@pytest.fixture(autouse=True)
def isolate_base_dir(tmp_path):
    pipeline_module.set_base_dir(tmp_path)
    yield
    pipeline_module.set_base_dir(None)
