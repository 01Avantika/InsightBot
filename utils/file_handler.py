"""
utils/file_handler.py — File saving, validation, and PDF text extraction
"""

import os
import hashlib
import pdfplumber
from pathlib import Path
from datetime import datetime

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "pdf"}
MAX_FILE_MB = 100


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def is_allowed_file(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def save_uploaded_file(file_bytes: bytes, filename: str, user_id: int) -> tuple[str, int]:
    """Save file to disk and return (path, size_bytes)."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Make unique filename to avoid collisions
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"user{user_id}_{ts}_{filename}"
    file_path = UPLOAD_DIR / safe_name

    file_path.write_bytes(file_bytes)
    return str(file_path), len(file_bytes)


def extract_pdf_text(file_path: str) -> str:
    """Extract all text from a PDF file."""
    text_parts = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                txt = page.extract_text()
                if txt:
                    text_parts.append(f"--- Page {i+1} ---\n{txt}")
    except Exception as e:
        return f"Error extracting PDF text: {e}"
    return "\n\n".join(text_parts)


def get_pdf_page_count(file_path: str) -> int:
    try:
        with pdfplumber.open(file_path) as pdf:
            return len(pdf.pages)
    except Exception:
        return 0


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / 1024**2:.1f} MB"
