import re
from datetime import datetime

from models.case_state import InternshipCaseState
from services.pdf_service import (
    extract_text_from_pdf,
    find_value_after_label,
)


STUDENT_ID_PATTERN = re.compile(r"\bATA\d+\b", re.IGNORECASE)

DATE_RANGE_PATTERN = re.compile(
    r"(?P<start>\d{2}\.\d{2}\.\d{4})"
    r"\s*[-–—]\s*"
    r"(?P<end>\d{2}\.\d{2}\.\d{4})"
)

EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)


def _non_empty_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def _extract_generated_template_fields(
    text: str,
) -> dict[str, str | None]:
    """
    Extract fields from the positional ATA test-dataset PDF.

    Expected beginning of extracted text:
    0: student name
    1: student ID
    2: field of study
    3: study cycle
    4: semester
    5: company name
    6: company address
    7: internship date range
    ...
    11: manager name, role, email, phone
    """

    lines = _non_empty_lines(text)

    fields: dict[str, str | None] = {
        "student_name": None,
        "student_id": None,
        "company_name": None,
        "supervisor_name": None,
        "supervisor_email": None,
        "internship_start_date": None,
        "internship_end_date": None,
    }

    student_id_index: int | None = None

    for index, line in enumerate(lines):
        match = STUDENT_ID_PATTERN.search(line)

        if match:
            fields["student_id"] = match.group(0)
            student_id_index = index
            break

    if student_id_index is not None:
        if student_id_index >= 1:
            fields["student_name"] = lines[
                student_id_index - 1
            ]

        company_index = student_id_index + 4

        if company_index < len(lines):
            fields["company_name"] = lines[company_index]

    date_match = DATE_RANGE_PATTERN.search(text)

    if date_match:
        fields["internship_start_date"] = (
            date_match.group("start")
        )
        fields["internship_end_date"] = (
            date_match.group("end")
        )

    for line in lines:
        email_match = EMAIL_PATTERN.search(line)

        if email_match is None or "," not in line:
            continue

        manager_parts = [
            part.strip()
            for part in line.split(",")
            if part.strip()
        ]

        if manager_parts:
            fields["supervisor_name"] = manager_parts[0]

        fields["supervisor_email"] = email_match.group(0)
        break

    return fields


def _label_or_fallback(
    text: str,
    label: str,
    fallback: str | None,
) -> str | None:
    labelled_value = find_value_after_label(text, label)

    if labelled_value:
        return labelled_value

    return fallback

def _normalize_date(
    value: str | None,
) -> str | None:
    if not value:
        return None

    value = value.strip()

    for date_format in (
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
    ):
        try:
            parsed_date = datetime.strptime(
                value,
                date_format,
            )

            return parsed_date.date().isoformat()

        except ValueError:
            continue

    return value

def document_extraction_agent(
    state: InternshipCaseState,
) -> InternshipCaseState:
    """
    Read the first PDF attachment and extract the application data.

    Supports:
    - Labelled text such as ``Student Name: Ayse Yilmaz``
    - Positional ATA generated-test-dataset PDFs
    """

    attachment_paths = state.get("attachment_paths", [])

    if not attachment_paths:
        state["status"] = "NO_ATTACHMENT_FOUND"
        state.setdefault("audit_log", []).append(
            f"[{datetime.now()}] Document Extraction Agent: "
            "No attachment found."
        )
        return state

    pdf_path = attachment_paths[0]
    text = extract_text_from_pdf(pdf_path)

    if text.startswith("PDF_EXTRACTION_ERROR:"):
        state["status"] = "DOCUMENT_EXTRACTION_FAILED"
        state.setdefault("audit_log", []).append(
            f"[{datetime.now()}] Document Extraction Agent: "
            f"{text}"
        )
        return state

    positional_fields = _extract_generated_template_fields(
        text
    )

    state["student_name"] = _label_or_fallback(
        text,
        "Student Name",
        positional_fields["student_name"],
    )

    state["student_id"] = _label_or_fallback(
        text,
        "Student ID",
        positional_fields["student_id"],
    )

    state["student_email"] = (
        find_value_after_label(text, "Student Email")
        or state.get("email_sender")
    )

    state["company_name"] = _label_or_fallback(
        text,
        "Company Name",
        positional_fields["company_name"],
    )

    state["supervisor_name"] = _label_or_fallback(
        text,
        "Supervisor Name",
        positional_fields["supervisor_name"],
    )

    state["supervisor_email"] = _label_or_fallback(
        text,
        "Supervisor Email",
        positional_fields["supervisor_email"],
    )

    state["internship_start_date"] = _normalize_date(
        _label_or_fallback(
            text,
            "Internship Start Date",
            positional_fields["internship_start_date"],
        )
    )

    state["internship_end_date"] = _normalize_date(
        _label_or_fallback(
            text,
            "Internship End Date",
            positional_fields["internship_end_date"],
        )
    )

    state["status"] = "DOCUMENT_EXTRACTED"

    state.setdefault("audit_log", []).append(
        f"[{datetime.now()}] Document Extraction Agent: "
        f"Extracted data from {pdf_path}."
    )

    return state
