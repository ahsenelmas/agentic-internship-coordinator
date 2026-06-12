import fitz
import re
from typing import Optional


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Reads a PDF file and returns all text.
    """

    text = ""

    try:
        document = fitz.open(pdf_path)

        for page in document:
            text += page.get_text()

        document.close()

    except Exception as e:
        text = f"PDF_EXTRACTION_ERROR: {str(e)}"

    return text


def find_value_after_label(text: str, label: str) -> Optional[str]:
    """
    Finds simple values written like:
    Student Name: Ahsen Nimet

    It reads only the value on the same line.
    """

    pattern = rf"{re.escape(label)}\s*:\s*([^\n\r]+)"
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return None


def extract_email(text: str) -> Optional[str]:
    """
    Extracts first email address from text.
    """

    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    if match:
        return match.group(0)

    return None
