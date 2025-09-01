# app/utils/ocr_utils.py
"""
OCR Utilities for PDF text extraction.

- Uses PyMuPDF (fitz) to grab native text where available.
- Falls back to Tesseract OCR on image-only pages.
- Returns per-page text as a dictionary: {page_number: text}.
"""

import io
from typing import Dict
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from .config import TESSERACT_CMD

# Configure pytesseract binary if provided in .env
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def page_to_image(page: fitz.Page, zoom: float = 2.0) -> Image.Image:
    """
    Render a PDF page to a PIL Image using PyMuPDF.
    - zoom=2.0 → ~144 DPI (higher zoom = better OCR but slower).
    """
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_bytes = pix.tobytes("png")
    return Image.open(io.BytesIO(img_bytes))


def extract_text_with_ocr(pdf_path: str, ocr_zoom: float = 2.5) -> Dict[int, str]:
    """
    Extract text from a PDF with fallback to OCR.
    - pdf_path: path to the PDF file
    - ocr_zoom: rendering scale used for OCR (higher -> better OCR at cost of speed)
    - Returns: {page_number: text}

    Workflow:
    1. Try extracting selectable text with page.get_text("text").
    2. If no text, render the page as an image and run Tesseract OCR.
    """
    doc = fitz.open(pdf_path)
    results: Dict[int, str] = {}

    for i, page in enumerate(doc, start=1):
        try:
            text = page.get_text("text") or ""
        except Exception:
            # Defensive: if PyMuPDF throws, fallback to OCR
            text = ""

        if text.strip():
            results[i] = text
            continue

        # Fallback to OCR
        image = page_to_image(page, zoom=ocr_zoom)
        ocr_text = pytesseract.image_to_string(image)
        results[i] = ocr_text

    return results
