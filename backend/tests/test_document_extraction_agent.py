import importlib
from typing import Any

import pytest


extraction_module = importlib.import_module(
    "agents.document_extraction_agent"
)


@pytest.mark.parametrize(
    ("input_date", "expected_date"),
    [
        ("05.10.2026", "2026-10-05"),
        ("05/10/2026", "2026-10-05"),
        ("2026-10-05", "2026-10-05"),
        (None, None),
    ],
)
def test_normalize_date(
    input_date: str | None,
    expected_date: str | None,
) -> None:
    result = extraction_module._normalize_date(
        input_date
    )

    assert result == expected_date


def test_generated_pdf_fields_are_extracted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    extracted_pdf_text = """
Kimberly Rodgers
ATA20267302
Computer Engineering
I
6
VertexDevelopment S.A.
927 Robert Springs, Grudziadz, Belgium
05.10.2026 - 19.12.2026
75 days
Web application development and database management
https://app-071-company.example.test
Sherri Williamson, Senior Software Developer, sherri.williamson.app-071-manager@example.test, +32 714097318
14.07.2026
Kimberly Rodgers
Sherri Williamson
"""

    def fake_extract_text_from_pdf(
        pdf_path: str,
    ) -> str:
        assert pdf_path == "APP-071_application.pdf"
        return extracted_pdf_text

    monkeypatch.setattr(
        extraction_module,
        "extract_text_from_pdf",
        fake_extract_text_from_pdf,
    )

    state: dict[str, Any] = {
        "email_sender": (
            "kimberly.rodgers.app-071@example.test"
        ),
        "email_subject": (
            "Workplace internship application - APP-071"
        ),
        "email_body": "Please find my application attached.",
        "attachment_paths": [
            "APP-071_application.pdf"
        ],
        "audit_log": [],
    }

    result = (
        extraction_module.document_extraction_agent(
            state
        )
    )

    assert result["status"] == "DOCUMENT_EXTRACTED"
    assert result["student_name"] == "Kimberly Rodgers"
    assert result["student_id"] == "ATA20267302"

    assert result["student_email"] == (
        "kimberly.rodgers.app-071@example.test"
    )

    assert result["company_name"] == (
        "VertexDevelopment S.A."
    )

    assert result["supervisor_name"] == (
        "Sherri Williamson"
    )

    assert result["supervisor_email"] == (
        "sherri.williamson.app-071-manager@example.test"
    )

    assert result["internship_start_date"] == (
        "2026-10-05"
    )

    assert result["internship_end_date"] == (
        "2026-12-19"
    )

    assert len(result["audit_log"]) == 1


def test_no_attachment_is_reported() -> None:
    state: dict[str, Any] = {
        "email_sender": "student@example.test",
        "email_subject": "Internship application",
        "email_body": "",
        "attachment_paths": [],
        "audit_log": [],
    }

    result = (
        extraction_module.document_extraction_agent(
            state
        )
    )

    assert result["status"] == "NO_ATTACHMENT_FOUND"
    assert len(result["audit_log"]) == 1
