from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import fitz


REQUIRED_CASE_FILES = [
    "case_data.json",
    "email.json",
    "email.txt",
    "expected_result.json",
]


def validate_json_file(path: Path) -> list[str]:
    errors = []

    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(
            f"Invalid JSON file {path.name}: {exc}"
        )

    return errors


def validate_pdf(
    pdf_path: Path,
    category: str,
    broken_type: str | None,
) -> list[str]:
    errors: list[str] = []

    if not pdf_path.exists():
        return [f"Missing PDF: {pdf_path.name}"]

    if pdf_path.stat().st_size == 0:
        return [f"PDF file is empty: {pdf_path.name}"]

    # Broken files are intentionally abnormal.
    if category == "broken":
        if broken_type == "invalid_pdf":
            try:
                document = fitz.open(pdf_path)
                document.close()

                # Some PDF readers may still try to recover unusual files.
                # For this test, check the file signature instead.
                file_header = pdf_path.read_bytes()[:5]

                if file_header == b"%PDF-":
                    errors.append(
                        f"{pdf_path.name} was expected to contain "
                        "invalid PDF data."
                    )

            except Exception:
                pass

            return errors

        if broken_type == "truncated_pdf":
            file_size = pdf_path.stat().st_size

            if file_size < 100:
                errors.append(
                    f"{pdf_path.name} is too small even for the "
                    "truncated-PDF test."
                )

            # A truncated PDF may still be recovered by PyMuPDF.
            # Its existence and intentionally reduced size are enough.
            return errors

        if broken_type == "blank_pdf":
            try:
                document = fitz.open(pdf_path)

                if document.page_count == 0:
                    errors.append(
                        f"{pdf_path.name} has no pages."
                    )

                document.close()

            except Exception as exc:
                errors.append(
                    f"Blank test PDF could not be opened: {exc}"
                )

            return errors

        if broken_type == "missing_pages":
            try:
                document = fitz.open(pdf_path)

                if document.page_count != 1:
                    errors.append(
                        f"{pdf_path.name} should contain exactly "
                        "one page for the missing-pages test."
                    )

                document.close()

            except Exception as exc:
                errors.append(
                    f"Missing-pages PDF could not be opened: {exc}"
                )

            return errors

        if broken_type == "blurred_scan":
            try:
                document = fitz.open(pdf_path)

                if document.page_count == 0:
                    errors.append(
                        f"{pdf_path.name} has no pages."
                    )

                document.close()

            except Exception as exc:
                errors.append(
                    f"Blurred PDF could not be opened: {exc}"
                )

            return errors

        errors.append(
            f"Unknown broken document type: {broken_type}"
        )
        return errors

    # All non-broken documents should open normally.
    try:
        document = fitz.open(pdf_path)

        if document.page_count == 0:
            errors.append(
                f"{pdf_path.name} has no pages."
            )

        document.close()

    except Exception as exc:
        errors.append(
            f"PDF could not be opened: {pdf_path.name}: {exc}"
        )

    return errors


def validate_case_folder(
    case_folder: Path,
) -> dict[str, Any]:
    errors = []

    for filename in REQUIRED_CASE_FILES:
        path = case_folder / filename

        if not path.exists():
            errors.append(
                f"Missing file: {filename}"
            )

    case_data_path = case_folder / "case_data.json"

    if not case_data_path.exists():
        return {
            "case_id": case_folder.name,
            "valid": False,
            "errors": errors,
        }

    errors.extend(
        validate_json_file(case_data_path)
    )

    try:
        case = json.loads(
            case_data_path.read_text(
                encoding="utf-8",
            )
        )
    except Exception:
        return {
            "case_id": case_folder.name,
            "valid": False,
            "errors": errors,
        }

    pdf_path = (
        case_folder
        / f"{case['case_id']}_application.pdf"
    )

    errors.extend(
        validate_pdf(
            pdf_path=pdf_path,
            category=case["primary_category"],
            broken_type=case.get("broken_type"),
        )
    )

    for filename in [
        "email.json",
        "expected_result.json",
    ]:
        path = case_folder / filename

        if path.exists():
            errors.extend(validate_json_file(path))

    return {
        "case_id": case["case_id"],
        "category": case["primary_category"],
        "valid": len(errors) == 0,
        "errors": errors,
    }


def validate_dataset(
    output_dir: Path,
) -> dict[str, Any]:
    case_folders = sorted(
        folder
        for folder in output_dir.iterdir()
        if folder.is_dir()
        and folder.name.startswith("APP-")
    )

    results = [
        validate_case_folder(folder)
        for folder in case_folders
    ]

    category_counts = Counter(
        result.get("category", "unknown")
        for result in results
    )

    valid_cases = sum(
        1 for result in results
        if result["valid"]
    )

    report = {
        "total_cases": len(results),
        "valid_cases": valid_cases,
        "invalid_cases": len(results) - valid_cases,
        "category_counts": dict(category_counts),
        "cases": results,
    }

    report_path = (
        output_dir
        / "dataset_validation_report.json"
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return report
