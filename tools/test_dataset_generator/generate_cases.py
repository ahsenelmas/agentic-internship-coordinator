from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from case_factory import apply_category, create_base_case
from config import (
    CATEGORY_COUNTS,
    OUTPUT_DIR,
    TEMPLATE_PATH,
    create_output_directory,
)
from email_generator import generate_email_files
from pdf_generator import generate_application_pdf
from validators import validate_dataset


def save_case_data(
    case: dict,
    case_folder: Path,
) -> None:
    """
    Save all generated synthetic data for one case.
    """
    case_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = case_folder / "case_data.json"

    output_path.write_text(
        json.dumps(
            case,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def save_manifest(
    cases: list[dict],
) -> None:
    """
    Create one CSV summary containing all generated cases.
    """
    manifest_path = OUTPUT_DIR / "dataset_manifest.csv"

    fieldnames = [
        "case_id",
        "primary_category",
        "expected_decision",
        "expected_security_flag",
        "expected_missing_fields",
        "expected_reason",
        "student_name",
        "student_id",
        "student_email",
        "company_name",
        "company_country",
        "internship_start",
        "internship_end",
        "manager_name",
        "broken_type",
        "clarification_type",
        "rejection_type",
        "handwriting_quality",
        "attachment_filename",
    ]

    with manifest_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for case in cases:
            writer.writerow(
                {
                    "case_id": case["case_id"],
                    "primary_category": case[
                        "primary_category"
                    ],
                    "expected_decision": case[
                        "expected_decision"
                    ],
                    "expected_security_flag": case.get(
                        "expected_security_flag",
                        False,
                    ),
                    "expected_missing_fields": ",".join(
                        case.get(
                            "expected_missing_fields",
                            [],
                        )
                    ),
                    "expected_reason": case[
                        "expected_reason"
                    ],
                    "student_name": case[
                        "student_name"
                    ],
                    "student_id": case[
                        "student_id"
                    ],
                    "student_email": case[
                        "student_email"
                    ],
                    "company_name": case[
                        "company_name"
                    ],
                    "company_country": case[
                        "company_country"
                    ],
                    "internship_start": case[
                        "internship_start"
                    ],
                    "internship_end": case[
                        "internship_end"
                    ],
                    "manager_name": case[
                        "manager_name"
                    ],
                    "broken_type": case.get(
                        "broken_type",
                        "",
                    ),
                    "clarification_type": case.get(
                        "clarification_type",
                        "",
                    ),
                    "rejection_type": case.get(
                        "rejection_type",
                        "",
                    ),
                    "handwriting_quality": case.get(
                        "handwriting_quality",
                        "",
                    ),
                    "attachment_filename": (
                        f"{case['case_id']}_application.pdf"
                    ),
                }
            )

    print(f"Manifest created: {manifest_path}")


def clear_old_dataset() -> None:
    """
    Delete the previous generated dataset before creating a new one.
    """
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    create_output_directory()


def build_category_list() -> list[str]:
    """
    Convert category counts into a list of exactly 100 categories.
    """
    categories: list[str] = []

    for category, count in CATEGORY_COUNTS.items():
        categories.extend(
            [category] * count
        )

    return categories


def generate_all_cases() -> None:
    """
    Generate the complete 100-case test dataset.
    """
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            "ATA template was not found.\n"
            f"Expected location: {TEMPLATE_PATH}"
        )

    clear_old_dataset()

    categories = build_category_list()

    expected_total = sum(
        CATEGORY_COUNTS.values()
    )

    if expected_total != 100:
        raise ValueError(
            "CATEGORY_COUNTS must add up to 100. "
            f"Current total: {expected_total}"
        )

    print("ATA template found.")
    print(
        f"Generating {expected_total} test cases...\n"
    )

    generated_cases: list[dict] = []

    for index, category in enumerate(
        categories,
        start=1,
    ):
        case_id = f"APP-{index:03d}"

        # Generate a normal synthetic application.
        case = create_base_case(case_id)

        # Apply the selected test category.
        case = apply_category(
            case,
            category,
        )

        # Create the folder for this case.
        case_folder = OUTPUT_DIR / case_id

        case_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Save the complete synthetic data.
        save_case_data(
            case,
            case_folder,
        )

        # Create the PDF attachment.
        pdf_path = (
            case_folder
            / f"{case_id}_application.pdf"
        )

        generate_application_pdf(
            case=case,
            template_path=TEMPLATE_PATH,
            output_path=pdf_path,
        )

        # Create email.json, email.txt,
        # and expected_result.json.
        generate_email_files(
            case=case,
            case_folder=case_folder,
            attachment_filename=pdf_path.name,
        )

        generated_cases.append(case)

        print(
            f"{case_id}: "
            f"{case['primary_category']} -> "
            f"{case['expected_decision']}"
        )

    save_manifest(generated_cases)

    validation_report = validate_dataset(
        OUTPUT_DIR
    )

    print("\nValidation results:")
    print(
        f"Valid cases: "
        f"{validation_report['valid_cases']}/"
        f"{validation_report['total_cases']}"
    )

    print(
        f"Invalid cases: "
        f"{validation_report['invalid_cases']}"
    )

    print("\nCategory counts:")

    for category, count in (
        validation_report[
            "category_counts"
        ].items()
    ):
        print(f"  {category}: {count}")

    if validation_report[
        "invalid_cases"
    ] > 0:
        print("\nValidation errors:")

        for result in validation_report["cases"]:
            if not result["valid"]:
                print(
                    f"\n{result['case_id']}:"
                )

                for error in result["errors"]:
                    print(f"  - {error}")

    print("\nFull dataset generation completed.")
    print(f"Output folder: {OUTPUT_DIR}")


def main() -> None:
    try:
        generate_all_cases()

    except FileNotFoundError as exc:
        print("\nERROR:")
        print(exc)

    except ValueError as exc:
        print("\nCONFIGURATION ERROR:")
        print(exc)

    except Exception as exc:
        print("\nUnexpected generation error:")
        print(
            f"{type(exc).__name__}: {exc}"
        )
        raise


if __name__ == "__main__":
    main()
