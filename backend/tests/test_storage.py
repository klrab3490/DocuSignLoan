import os
import pytest
from fastapi import UploadFile
from app.utils.storage import save_file_permanent, delete_temp_file

class DummyFile:
    def __init__(self, content: bytes):
        self.file = io.BytesIO(content)
        self.filename = "dummy.pdf"

import io

@pytest.mark.asyncio
async def test_save_and_delete_file(tmp_path, monkeypatch):
    monkeypatch.setattr("app.utils.storage.UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr("app.utils.storage.UPLOAD_DIR_temp", str(tmp_path / "temp"))
    os.makedirs(tmp_path / "temp", exist_ok=True)

    dummy = DummyFile(b"fake pdf content")
    file_paths = await save_file_permanent(dummy)
    assert os.path.exists(file_paths[0])
    assert os.path.exists(file_paths[1])

    await delete_temp_file(dummy)
    assert not os.path.exists(file_paths[1])
