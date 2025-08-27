import sys
import os
import sys
import os
# Ensure 'backend' is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app.utils.file_utils import sanitize_filename

def test_sanitize_filename_valid():
    assert sanitize_filename("document.pdf") == "document.pdf"

def test_sanitize_filename_invalid_extension():
    with pytest.raises(ValueError):
        sanitize_filename("malicious.exe")

def test_sanitize_filename_with_path_traversal():
    with pytest.raises(ValueError):
        sanitize_filename("../secret.pdf")
