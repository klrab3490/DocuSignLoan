# app/utils/ocr_utils.py
"""
OCR Utilities for PDF text extraction.

- Uses PyMuPDF (fitz) to grab native text where available.
- Falls back to Tesseract OCR on image-only pages.
- Cleans OCR output to reduce noise.
- Returns per-page text as a dictionary: {page_number: text}.
"""

import io
import re
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
    """
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_bytes = pix.tobytes("png")
    return Image.open(io.BytesIO(img_bytes))


def clean_ocr_text(text: str) -> str:
    """
    Clean OCR text by removing noise, redundant spaces,
    and common header/footer patterns.
    """
    if not text:
        return ""

    # Normalize line breaks
    text = text.replace("\r", "\n")

    # Remove multiple consecutive newlines
    text = re.sub(r"\n{2,}", "\n", text)

    # Remove page numbers like "Page 12", "12/400"
    text = re.sub(r"(Page\s*\d+)|(\d+\s*/\s*\d+)", "", text, flags=re.IGNORECASE)

    # Remove extra non-ASCII junk characters
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()


def extract_text_with_ocr(pdf_path: str, ocr_zoom: float = 2.5) -> Dict[int, str]:
    """
    Extract text from a PDF, using native text where possible,
    and Tesseract OCR for image-only pages.
    Cleans OCR output before returning.
    """
    doc = fitz.open(pdf_path)
    results: Dict[int, str] = {}

    for page_number, page in enumerate(doc, start=1):
        text = ""
        try:
            text = page.get_text("text") or ""
        except Exception:
            pass  # fallback to OCR if PyMuPDF fails

        if text.strip():
            results[page_number] = clean_ocr_text(text)
            continue

        # Fallback to OCR
        try:
            image = page_to_image(page, zoom=ocr_zoom)
            ocr_text = pytesseract.image_to_string(image)
            results[page_number] = clean_ocr_text(ocr_text)
        except Exception:
            results[page_number] = ""

    return results
