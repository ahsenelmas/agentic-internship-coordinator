from datetime import datetime
from typing import Any


MIN_INTERNSHIP_DAYS = 20

EU_COUNTRIES = {
    "austria",
    "belgium",
    "bulgaria",
    "croatia",
    "cyprus",
    "czech republic",
    "czechia",
    "denmark",
    "estonia",
    "finland",
    "france",
    "germany",
    "greece",
    "hungary",
    "ireland",
    "italy",
    "latvia",
    "lithuania",
    "luxembourg",
    "malta",
    "netherlands",
    "poland",
    "portugal",
    "romania",
    "slovakia",
    "slovenia",
    "spain",
    "sweden",
}


def parse_date(
    date_text: str,
) -> datetime | None:
    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d",
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def validate_university_rules(
    case_data: dict[str, Any],
) -> dict[str, Any]:
    violations: list[str] = []

    start_date = parse_date(
        case_data.get(
            "internship_start_date",
            "",
        )
    )

    end_date = parse_date(
        case_data.get(
            "internship_end_date",
            "",
        )
    )

    if not start_date or not end_date:
        violations.append(
            "Internship start date or end date "
            "is missing or invalid."
        )

    else:
        if end_date <= start_date:
            violations.append(
                "Internship end date must be "
                "after start date."
            )

        duration = (
            end_date - start_date
        ).days

        if duration < MIN_INTERNSHIP_DAYS:
            violations.append(
                "Internship duration is too short. "
                f"Minimum is {MIN_INTERNSHIP_DAYS} days."
            )

    company_country = str(
        case_data.get(
            "company_country",
            "",
        )
        or ""
    ).strip()

    if (
        company_country
        and company_country.casefold()
        not in EU_COUNTRIES
    ):
        violations.append(
            "The internship company must be "
            "located in an EU member country."
        )

    return {
        "valid": len(violations) == 0,
        "violations": violations,
    }
