import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from main import app  # Now this works
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    response = client.get("/pdf/status")
    assert response.status_code in (200, 401)  # 401 if auth required
