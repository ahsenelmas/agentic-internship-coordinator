from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def create_email_data(
    case: dict[str, Any],
    attachment_filename: str,
) -> dict[str, Any]:
    return {
        "case_id": case["case_id"],
        "from": case["student_email"],
        "to": "internships@ata.example.test",
        "subject": case["email_subject"],
        "body": case["email_body"],
        "attachments": [attachment_filename],
    }


def create_expected_result(
    case: dict[str, Any],
) -> dict[str, Any]:
    return {
        "case_id": case["case_id"],
        "primary_category": case["primary_category"],
        "secondary_tags": case.get("secondary_tags", []),
        "expected_decision": case["expected_decision"],
        "expected_reason": case["expected_reason"],
        "expected_missing_fields": case.get(
            "expected_missing_fields",
            [],
        ),
        "expected_security_flag": case.get(
            "expected_security_flag",
            False,
        ),
        "broken_type": case.get("broken_type"),
        "clarification_type": case.get("clarification_type"),
        "rejection_type": case.get("rejection_type"),
        "handwriting_quality": case.get("handwriting_quality"),
    }


def save_json(
    data: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def generate_email_files(
    case: dict[str, Any],
    case_folder: Path,
    attachment_filename: str,
) -> None:
    email_data = create_email_data(
        case,
        attachment_filename,
    )

    expected_result = create_expected_result(case)

    save_json(
        email_data,
        case_folder / "email.json",
    )

    save_json(
        expected_result,
        case_folder / "expected_result.json",
    )

    email_text = (
        f"From: {email_data['from']}\n"
        f"To: {email_data['to']}\n"
        f"Subject: {email_data['subject']}\n"
        f"Attachment: {attachment_filename}\n\n"
        f"{email_data['body']}\n"
    )

    (case_folder / "email.txt").write_text(
        email_text,
        encoding="utf-8",
    )
