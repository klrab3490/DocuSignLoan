import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_job_status_not_found():
    response = client.get("/pdf/jobs/fake-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

def test_get_all_jobs():
    response = client.get("/pdf/status")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
