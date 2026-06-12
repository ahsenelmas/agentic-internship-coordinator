from datetime import datetime


MIN_INTERNSHIP_DAYS = 20


def parse_date(date_text: str):
    try:
        return datetime.strptime(date_text, "%Y-%m-%d")
    except Exception:
        return None


def validate_university_rules(case_data: dict) -> dict:
    violations = []

    start_date = parse_date(case_data.get("internship_start_date", ""))
    end_date = parse_date(case_data.get("internship_end_date", ""))

    if not start_date or not end_date:
        violations.append("Internship start date or end date is missing or invalid.")
    else:
        if end_date <= start_date:
            violations.append("Internship end date must be after start date.")

        duration = (end_date - start_date).days

        if duration < MIN_INTERNSHIP_DAYS:
            violations.append(
                f"Internship duration is too short. Minimum is {MIN_INTERNSHIP_DAYS} days."
            )

    return {
        "valid": len(violations) == 0,
        "violations": violations
    }
