import os
import json
import pytest
from app.utils import save_jobs_to_file, load_jobs_from_file

def test_save_and_load_jobs(tmp_path, monkeypatch):
    test_file = tmp_path / "jobs.json"
    monkeypatch.setattr("app.utils.jobs.job_file", str(test_file))

    jobs_data = {"123": {"status": "processing", "filename": "test.pdf"}}
    save_jobs_to_file(jobs_data)

    loaded = load_jobs_from_file()
    assert "123" in loaded
    assert loaded["123"]["status"] == "processing"
