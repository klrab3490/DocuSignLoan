import io
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_extract_and_format_invalid_filetype():
    response = client.post(
        "/pdf/extract-and-format/",
        files={"file": ("test.txt", b"not a pdf", "text/plain")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file type. Please upload a PDF."
