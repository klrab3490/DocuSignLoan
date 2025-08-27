import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_highlight_text_invalid_job():
    response = client.get("pdf/highlight/", params={"job_id": "fake", "page_number": 1, "query": "test"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
