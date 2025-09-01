# app/__init__.py
"""
App package initializer.

This package contains:
- api: FastAPI route handlers
- utils: configuration, OCR, schema, merging, storage
- workflows: LangGraph pipelines for PDF extraction
"""

from .utils import (
    config,
    file_utils,
    jobs,
    storage,
    ocr_utils,
    merge_utils,
    schema,
)
from .workflows import pdf_pipeline

__all__ = [
    "config",
    "file_utils",
    "jobs",
    "storage",
    "ocr_utils",
    "merge_utils",
    "schema",
    "pdf_pipeline",
]
