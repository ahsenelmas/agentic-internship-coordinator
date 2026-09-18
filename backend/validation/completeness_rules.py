from typing import Any


REQUIRED_FIELDS = [
    "student_name",
    "student_id",
    "student_email",
    "student_signature",
    "company_name",
    "supervisor_name",
    "supervisor_email",
    "internship_start_date",
    "internship_end_date",
]


def check_completeness(
    case_data: dict[str, Any],
) -> dict[str, Any]:
    missing_fields: list[str] = []

    for field in REQUIRED_FIELDS:
        value = case_data.get(field)

        if value is None or str(value).strip() == "":
            missing_fields.append(field)

    return {
        "complete": len(missing_fields) == 0,
        "missing_fields": missing_fields,
    }
