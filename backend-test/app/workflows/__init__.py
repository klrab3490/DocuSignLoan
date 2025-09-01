# app/workflows/__init__.py
"""
Workflows package initializer.

Currently includes:
- pdf_pipeline: Hybrid pipeline for OCR + Gemini schema extraction
"""

from .pdf_pipeline import run_pipeline_on_pdf

__all__ = ["run_pipeline_on_pdf"]
