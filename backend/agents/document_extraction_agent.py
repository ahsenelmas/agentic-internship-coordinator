import re
from datetime import datetime
from typing import Any

from models.case_state import InternshipCaseState
from services.pdf_service import (
    extract_text_from_pdf,
    find_value_after_label,
)


STUDENT_ID_PATTERN = re.compile(
    r"\bATA\d+\b",
    re.IGNORECASE,
)

DATE_PATTERN = re.compile(
    r"\b\d{2}\.\d{2}\.\d{4}\b"
)

DATE_RANGE_PATTERN = re.compile(
    r"(?P<start>\d{2}\.\d{2}\.\d{4})"
    r"\s*[-–—]\s*"
    r"(?P<end>\d{2}\.\d{2}\.\d{4})"
)

EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@"
    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

ADDRESS_PATTERN = re.compile(
    r"^(?:"
    r"ul\.?|ulica|aleja|al\.?|"
    r"plac|pl\.?|street|st\.?|"
    r"road|rd\.?|avenue|ave\.?|"
    r"boulevard|blvd\.?"
    r")\s+",
    re.IGNORECASE,
)

WEEKLY_HOURS_PATTERN = re.compile(
    r"(?P<value>"
    r"(?:approximately|about|around|between)?"
    r"\s*\d+"
    r"\s*(?:[-–—]\s*\d+)?"
    r"\s*hours?"
    r")",
    re.IGNORECASE,
)

SECURITY_PATTERNS = [
    re.compile(
        r"ignore\s+(?:all\s+)?"
        r"(?:previous|prior)\s+instructions",
        re.IGNORECASE,
    ),
    re.compile(
        r"disregard\s+(?:all\s+)?"
        r"(?:previous|prior)\s+instructions",
        re.IGNORECASE,
    ),
    re.compile(
        r"override\s+(?:all\s+)?instructions",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bsystem\s+prompt\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bprompt\s+injection\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:mark|set|classify)"
        r".{0,80}"
        r"\b(?:approve|approved|reject|rejected)\b",
        re.IGNORECASE | re.DOTALL,
    ),
]


def _non_empty_lines(
    text: str,
) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def _normalize_text(
    value: str,
) -> str:
    return " ".join(
        value.casefold().split()
    )


def _normalize_date(
    value: str | None,
) -> str | None:
    if not value:
        return None

    cleaned_value = value.strip()

    for date_format in (
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
    ):
        try:
            parsed_date = datetime.strptime(
                cleaned_value,
                date_format,
            )

            return parsed_date.date().isoformat()

        except ValueError:
            continue

    return cleaned_value


def _looks_like_address(
    value: str | None,
) -> bool:
    if not value:
        return False

    if ADDRESS_PATTERN.search(value):
        return True

    return (
        "," in value
        and bool(re.search(r"\d", value))
    )


def _extract_country(
    address: str | None,
) -> str | None:
    if not address or "," not in address:
        return None

    country = address.rsplit(
        ",",
        maxsplit=1,
    )[-1].strip()

    return country or None


def _detect_security_reasons(
    text: str,
    email_subject: str,
    email_body: str,
) -> list[str]:
    combined_content = "\n".join(
        [
            text,
            email_subject,
            email_body,
        ]
    )

    reasons: list[str] = []

    for pattern in SECURITY_PATTERNS:
        if pattern.search(combined_content):
            reasons.append(
                "The application contains instruction-like "
                "content that may attempt to manipulate "
                "the automated review."
            )
            break

    return reasons


def _extract_weekly_hours(
    text: str,
    email_body: str,
) -> tuple[str | None, bool]:
    labelled_hours = (
        find_value_after_label(
            text,
            "Weekly Hours",
        )
        or find_value_after_label(
            text,
            "Weekly Working Hours",
        )
    )

    candidate = labelled_hours

    if not candidate:
        match = WEEKLY_HOURS_PATTERN.search(
            email_body
        )

        if match:
            candidate = match.group("value").strip()

    if not candidate:
        return None, False

    normalized_candidate = (
        candidate.casefold()
    )

    unclear = (
        any(
            qualifier in normalized_candidate
            for qualifier in (
                "approximately",
                "about",
                "around",
                "between",
            )
        )
        or bool(
            re.search(
                r"\d+\s*[-–—]\s*\d+",
                candidate,
            )
        )
    )

    return candidate, unclear


def _extract_generated_template_fields(
    text: str,
) -> tuple[
    dict[str, str | None],
    list[str],
]:
    lines = _non_empty_lines(text)
    warnings: list[str] = []

    fields: dict[str, str | None] = {
        "student_name": None,
        "student_id": None,
        "student_signature": None,
        "company_name": None,
        "company_address": None,
        "company_country": None,
        "supervisor_name": None,
        "supervisor_email": None,
        "internship_start_date": None,
        "internship_end_date": None,
    }

    student_id_index: int | None = None

    for index, line in enumerate(lines):
        match = STUDENT_ID_PATTERN.search(line)

        if match:
            fields["student_id"] = (
                match.group(0)
            )
            student_id_index = index
            break

    if student_id_index is not None:
        if student_id_index >= 1:
            fields["student_name"] = lines[
                student_id_index - 1
            ]

        cycle_index = student_id_index + 2
        cycle_value = (
            lines[cycle_index]
            if cycle_index < len(lines)
            else None
        )

        expected_cycles = {
            "I",
            "II",
            "III",
        }

        if cycle_value in expected_cycles:
            company_index = (
                student_id_index + 4
            )
            address_index = (
                student_id_index + 5
            )
        else:
            company_index = (
                student_id_index + 3
            )
            address_index = (
                student_id_index + 4
            )

            warnings.append(
                "The study-cycle field could not be "
                "reliably extracted from the document."
            )

        company_candidate = (
            lines[company_index]
            if company_index < len(lines)
            else None
        )

        address_candidate = (
            lines[address_index]
            if address_index < len(lines)
            else None
        )

        if _looks_like_address(
            company_candidate
        ):
            fields["company_name"] = None
            fields["company_address"] = (
                company_candidate
            )

            warnings.append(
                "The company name is missing or was "
                "confused with the company address."
            )

        else:
            fields["company_name"] = (
                company_candidate
            )
            fields["company_address"] = (
                address_candidate
            )

        fields["company_country"] = (
            _extract_country(
                fields["company_address"]
            )
        )

    date_match = DATE_RANGE_PATTERN.search(
        text
    )

    if date_match:
        fields["internship_start_date"] = (
            date_match.group("start")
        )
        fields["internship_end_date"] = (
            date_match.group("end")
        )

    for line in lines:
        email_match = EMAIL_PATTERN.search(
            line
        )

        if (
            email_match is None
            or "," not in line
        ):
            continue

        manager_parts = [
            part.strip()
            for part in line.split(",")
            if part.strip()
        ]

        if manager_parts:
            fields["supervisor_name"] = (
                manager_parts[0]
            )

        fields["supervisor_email"] = (
            email_match.group(0)
        )
        break

    student_name = fields["student_name"]

    if student_name:
        normalized_name = _normalize_text(
            student_name
        )

        name_occurrences = sum(
            _normalize_text(line)
            == normalized_name
            for line in lines
        )

        if name_occurrences >= 2:
            fields["student_signature"] = (
                student_name
            )

    return fields, warnings


def _label_or_fallback(
    text: str,
    label: str,
    fallback: str | None,
) -> str | None:
    labelled_value = find_value_after_label(
        text,
        label,
    )

    if labelled_value:
        return labelled_value

    return fallback


def _find_email_date_conflicts(
    email_body: str,
    start_date: str | None,
    end_date: str | None,
) -> list[str]:
    accepted_dates = {
        date
        for date in (
            start_date,
            end_date,
        )
        if date
    }

    email_dates = {
        _normalize_date(value)
        for value in DATE_PATTERN.findall(
            email_body
        )
    }

    conflicting_dates = {
        date
        for date in email_dates
        if date
        and date not in accepted_dates
    }

    return sorted(conflicting_dates)


def document_extraction_agent(
    state: InternshipCaseState,
) -> InternshipCaseState:
    """
    Read and analyse the first PDF attachment.

    The analysis includes:
    - Core field extraction
    - Signature presence
    - Template/extraction quality
    - Prompt-injection indicators
    - Email/PDF date consistency
    - Weekly-hours clarity
    """

    attachment_paths = state.get(
        "attachment_paths",
        [],
    )

    if not attachment_paths:
        state["status"] = (
            "NO_ATTACHMENT_FOUND"
        )
        state["security_flag"] = False
        state["security_reasons"] = []
        state["extraction_warnings"] = []

        state.setdefault(
            "audit_log",
            [],
        ).append(
            f"[{datetime.now()}] "
            "Document Extraction Agent: "
            "No attachment found."
        )

        return state

    pdf_path = attachment_paths[0]
    text = extract_text_from_pdf(pdf_path)

    if text.startswith(
        "PDF_EXTRACTION_ERROR:"
    ):
        state["status"] = (
            "DOCUMENT_EXTRACTION_FAILED"
        )
        state["security_flag"] = False
        state["security_reasons"] = []
        state["extraction_warnings"] = [
            text
        ]
        state["clarification_needed"] = True

        state.setdefault(
            "audit_log",
            [],
        ).append(
            f"[{datetime.now()}] "
            "Document Extraction Agent: "
            f"{text}"
        )

        return state

    (
        positional_fields,
        extraction_warnings,
    ) = _extract_generated_template_fields(
        text
    )

    state["student_name"] = (
        _label_or_fallback(
            text,
            "Student Name",
            positional_fields[
                "student_name"
            ],
        )
    )

    state["student_id"] = (
        _label_or_fallback(
            text,
            "Student ID",
            positional_fields[
                "student_id"
            ],
        )
    )

    state["student_email"] = (
        find_value_after_label(
            text,
            "Student Email",
        )
        or state.get("email_sender")
    )

    state["student_signature"] = (
        _label_or_fallback(
            text,
            "Student Signature",
            positional_fields[
                "student_signature"
            ],
        )
    )

    state["company_name"] = (
        _label_or_fallback(
            text,
            "Company Name",
            positional_fields[
                "company_name"
            ],
        )
    )

    state["company_address"] = (
        _label_or_fallback(
            text,
            "Company Address",
            positional_fields[
                "company_address"
            ],
        )
    )

    state["company_country"] = (
        find_value_after_label(
            text,
            "Company Country",
        )
        or positional_fields[
            "company_country"
        ]
    )

    state["supervisor_name"] = (
        _label_or_fallback(
            text,
            "Supervisor Name",
            positional_fields[
                "supervisor_name"
            ],
        )
    )

    state["supervisor_email"] = (
        _label_or_fallback(
            text,
            "Supervisor Email",
            positional_fields[
                "supervisor_email"
            ],
        )
    )

    state["internship_start_date"] = (
        _normalize_date(
            _label_or_fallback(
                text,
                "Internship Start Date",
                positional_fields[
                    "internship_start_date"
                ],
            )
        )
    )

    state["internship_end_date"] = (
        _normalize_date(
            _label_or_fallback(
                text,
                "Internship End Date",
                positional_fields[
                    "internship_end_date"
                ],
            )
        )
    )

    email_subject = state.get(
        "email_subject",
        "",
    )
    email_body = state.get(
        "email_body",
        "",
    )

    security_reasons = (
        _detect_security_reasons(
            text=text,
            email_subject=email_subject,
            email_body=email_body,
        )
    )

    state["security_flag"] = bool(
        security_reasons
    )
    state["security_reasons"] = (
        security_reasons
    )

    conflicting_dates = (
        _find_email_date_conflicts(
            email_body=email_body,
            start_date=state.get(
                "internship_start_date"
            ),
            end_date=state.get(
                "internship_end_date"
            ),
        )
    )

    if conflicting_dates:
        extraction_warnings.append(
            "The internship date stated in the "
            "email conflicts with the PDF: "
            + ", ".join(conflicting_dates)
            + "."
        )

    weekly_hours, hours_unclear = (
        _extract_weekly_hours(
            text=text,
            email_body=email_body,
        )
    )

    state["weekly_hours"] = (
        weekly_hours
    )

    if hours_unclear:
        extraction_warnings.append(
            "The weekly working hours are "
            "not clearly defined."
        )

    state["extraction_warnings"] = (
        extraction_warnings
    )

    state["clarification_needed"] = (
        bool(
            state.get(
                "clarification_needed",
                False,
            )
        )
        or bool(extraction_warnings)
        or bool(security_reasons)
    )

    state["status"] = (
        "DOCUMENT_REVIEW_REQUIRED"
        if state["clarification_needed"]
        else "DOCUMENT_EXTRACTED"
    )

    state.setdefault(
        "audit_log",
        [],
    ).append(
        f"[{datetime.now()}] "
        "Document Extraction Agent: "
        f"Extracted and analysed {pdf_path}."
    )

    return state
