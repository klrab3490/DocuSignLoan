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
    
    Parameters:
        page: PyMuPDF Page object
        zoom: Rendering scale (2.0 ~ 144 DPI). Higher zoom -> better OCR.
    
    Returns:
        PIL Image of the page.
    """
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_bytes = pix.tobytes("png")
    return Image.open(io.BytesIO(img_bytes))


def extract_text_with_ocr(pdf_path: str, ocr_zoom: float = 2.5) -> Dict[int, str]:
    """
    Extract text from a PDF, using native text where possible,
    and Tesseract OCR for image-only pages.
    
    Parameters:
        pdf_path: Path to the PDF file
        ocr_zoom: Rendering scale used for OCR
    
    Returns:
        Dict[int, str]: Mapping from page_number to extracted text.
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
            results[page_number] = text
            continue

        # Fallback to OCR
        try:
            image = page_to_image(page, zoom=ocr_zoom)
            ocr_text = pytesseract.image_to_string(image)
            results[page_number] = ocr_text
        except Exception:
            results[page_number] = ""  # fallback if OCR fails

    return results
