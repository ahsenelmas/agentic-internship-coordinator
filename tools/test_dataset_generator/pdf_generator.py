from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import fitz


TEXT_COLOR = (0.05, 0.08, 0.25)
HANDWRITING_COLOR = (0.08, 0.12, 0.45)


def add_text(
    page: fitz.Page,
    x: float,
    y: float,
    text: Any,
    *,
    fontsize: float = 10,
    color: tuple[float, float, float] = TEXT_COLOR,
) -> None:
    """Add one line of text to a PDF page."""
    if text is None:
        return

    value = str(text).strip()

    if not value:
        return

    page.insert_text(
        fitz.Point(x, y),
        value,
        fontsize=fontsize,
        color=color,
        fontname="helv",
        overlay=True,
    )


def add_textbox(
    page: fitz.Page,
    rect: tuple[float, float, float, float],
    text: Any,
    *,
    fontsize: float = 9,
    color: tuple[float, float, float] = TEXT_COLOR,
) -> None:
    """Add wrapped text inside a fixed rectangle."""
    if text is None:
        return

    value = str(text).strip()

    if not value:
        return

    page.insert_textbox(
        fitz.Rect(*rect),
        value,
        fontsize=fontsize,
        color=color,
        fontname="helv",
        align=fitz.TEXT_ALIGN_LEFT,
        overlay=True,
    )


def create_normal_pdf(
    case: dict[str, Any],
    template_path: Path,
    output_path: Path,
) -> None:
    document = fitz.open(template_path)

    if len(document) < 3:
        document.close()
        raise ValueError("The ATA template must contain at least three pages.")

    page_1 = document[0]
    page_2 = document[1]
    page_3 = document[2]

    # ---------------------------------------------------------
    # PAGE 1 - Student and workplace information
    # ---------------------------------------------------------

    add_text(page_1, 235, 158, case.get("student_name"), fontsize=9)
    add_text(page_1, 635, 158, case.get("application_date"), fontsize=9)

    add_text(page_1, 175, 187, case.get("student_id"), fontsize=9)
    add_text(page_1, 455, 187, case.get("field_of_study"), fontsize=9)

    add_text(page_1, 175, 215, case.get("cycle_of_study"), fontsize=9)
    add_text(page_1, 455, 215, case.get("semester"), fontsize=9)

    company_text = (
        f"{case.get('company_name', '')}\n"
        f"{case.get('company_address', '')}"
    )

    add_textbox(
        page_1,
        (48, 400, 550, 445),
        company_text,
        fontsize=8.5,
    )

    internship_period = (
        f"{case.get('internship_start', '')} - "
        f"{case.get('internship_end', '')}"
    )

    add_text(page_1, 235, 462, internship_period, fontsize=8.5)
    add_text(
        page_1,
        370,
        492,
        case.get("internship_duration"),
        fontsize=8.5,
    )

    add_textbox(
        page_1,
        (55, 520, 560, 605),
        case.get("company_activity"),
        fontsize=8.2,
    )

    add_textbox(
        page_1,
        (55, 687, 560, 720),
        case.get("company_website"),
        fontsize=8.3,
    )

    manager_details = (
        f"{case.get('manager_name', '')}, "
        f"{case.get('manager_role', '')}, "
        f"{case.get('manager_email', '')}, "
        f"{case.get('manager_phone', '')}"
    )

    add_textbox(
        page_1,
        (55, 750, 560, 805),
        manager_details,
        fontsize=7.7,
    )

    # ---------------------------------------------------------
    # PAGE 2 - Student confirmation and company confirmation
    # ---------------------------------------------------------

    add_text(page_2, 62, 146, case.get("application_date"), fontsize=9)
    add_text(
        page_2,
        430,
        146,
        case.get("student_signature"),
        fontsize=9,
    )

    add_text(page_2, 58, 245, case.get("manager_name"), fontsize=9)

    add_textbox(
        page_2,
        (55, 285, 560, 395),
        case.get("manager_comments"),
        fontsize=8.2,
    )

    add_text(page_2, 62, 430, case.get("application_date"), fontsize=9)

    add_text(
        page_2,
        430,
        430,
        case.get("manager_signature"),
        fontsize=9,
    )

    add_text(
        page_2,
        65,
        505,
        case.get("company_name"),
        fontsize=8.5,
    )

    # ---------------------------------------------------------
    # PAGE 3 - Student statement
    # ---------------------------------------------------------

    add_text(
        page_3,
        185,
        224,
        case.get("field_of_study"),
        fontsize=9,
    )

    add_text(
        page_3,
        470,
        224,
        case.get("cycle_of_study"),
        fontsize=9,
    )

    add_text(
        page_3,
        60,
        305,
        case.get("application_date"),
        fontsize=9,
    )

    add_text(
        page_3,
        430,
        305,
        case.get("student_signature"),
        fontsize=9,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    document.save(
        output_path,
        garbage=4,
        deflate=True,
    )
    document.close()


def create_blank_pdf(output_path: Path) -> None:
    document = fitz.open()
    document.new_page(width=595, height=842)
    document.save(output_path)
    document.close()


def create_invalid_pdf(output_path: Path) -> None:
    output_path.write_bytes(
        b"This file intentionally contains invalid PDF data."
    )


def create_truncated_pdf(
    template_path: Path,
    output_path: Path,
) -> None:
    content = template_path.read_bytes()

    truncated_size = max(100, len(content) // 4)

    output_path.write_bytes(content[:truncated_size])


def create_missing_pages_pdf(
    case: dict[str, Any],
    template_path: Path,
    output_path: Path,
) -> None:
    temporary_path = output_path.with_name(
        f"{output_path.stem}_temporary.pdf"
    )

    create_normal_pdf(case, template_path, temporary_path)

    source_document = fitz.open(temporary_path)
    output_document = fitz.open()

    # Keep only page 1.
    output_document.insert_pdf(
        source_document,
        from_page=0,
        to_page=0,
    )

    output_document.save(output_path)

    output_document.close()
    source_document.close()
    temporary_path.unlink(missing_ok=True)


def create_blurred_scan_pdf(
    case: dict[str, Any],
    template_path: Path,
    output_path: Path,
) -> None:
    temporary_path = output_path.with_name(
        f"{output_path.stem}_normal.pdf"
    )

    create_normal_pdf(case, template_path, temporary_path)

    document = fitz.open(temporary_path)
    blurred_document = fitz.open()

    for page in document:
        pixmap = page.get_pixmap(matrix=fitz.Matrix(0.55, 0.55))

        image_bytes = pixmap.tobytes("png")

        new_page = blurred_document.new_page(
            width=page.rect.width,
            height=page.rect.height,
        )

        new_page.insert_image(
            new_page.rect,
            stream=image_bytes,
        )

    blurred_document.save(output_path)

    blurred_document.close()
    document.close()
    temporary_path.unlink(missing_ok=True)


def create_broken_pdf(
    case: dict[str, Any],
    template_path: Path,
    output_path: Path,
) -> None:
    broken_type = case.get("broken_type", "blank_pdf")

    if broken_type == "blank_pdf":
        create_blank_pdf(output_path)

    elif broken_type == "invalid_pdf":
        create_invalid_pdf(output_path)

    elif broken_type == "truncated_pdf":
        create_truncated_pdf(template_path, output_path)

    elif broken_type == "missing_pages":
        create_missing_pages_pdf(
            case,
            template_path,
            output_path,
        )

    elif broken_type == "blurred_scan":
        create_blurred_scan_pdf(
            case,
            template_path,
            output_path,
        )

    else:
        raise ValueError(f"Unknown broken document type: {broken_type}")


def create_handwritten_pdf(
    case: dict[str, Any],
    template_path: Path,
    output_path: Path,
) -> None:
    """
    First pilot version.

    This version uses blue text with small rotations to imitate handwriting.
    We can improve the handwriting appearance after checking the pilot.
    """
    document = fitz.open(template_path)

    page_1 = document[0]
    page_2 = document[1]
    page_3 = document[2]

    color = HANDWRITING_COLOR

    def handwritten(
        page: fitz.Page,
        x: float,
        y: float,
        text: Any,
        fontsize: float = 10,
        rotate: int = 0,
    ) -> None:
        if text is None or not str(text).strip():
            return

        rect = fitz.Rect(x, y - 12, x + 360, y + 12)

        page.insert_textbox(
            rect,
            str(text),
            fontsize=fontsize,
            color=color,
            fontname="helv",
            rotate=rotate,
            overlay=True,
        )

    handwritten(page_1, 235, 158, case.get("student_name"), 9)
    handwritten(page_1, 635, 158, case.get("application_date"), 9)
    handwritten(page_1, 175, 187, case.get("student_id"), 9)
    handwritten(page_1, 455, 187, case.get("field_of_study"), 9)
    handwritten(page_1, 455, 215, case.get("semester"), 9)

    handwritten(page_1, 55, 415, case.get("company_name"), 8.5)
    handwritten(page_1, 55, 437, case.get("company_address"), 8)

    handwritten(
        page_1,
        235,
        462,
        (
            f"{case.get('internship_start', '')} - "
            f"{case.get('internship_end', '')}"
        ),
        8.5,
    )

    handwritten(
        page_1,
        370,
        492,
        case.get("internship_duration"),
        8.5,
    )

    add_textbox(
        page_1,
        (55, 520, 560, 605),
        case.get("company_activity"),
        fontsize=8.2,
        color=color,
    )

    handwritten(
        page_1,
        55,
        700,
        case.get("company_website"),
        8.2,
    )

    add_textbox(
        page_1,
        (55, 750, 560, 805),
        (
            f"{case.get('manager_name', '')}, "
            f"{case.get('manager_role', '')}, "
            f"{case.get('manager_email', '')}, "
            f"{case.get('manager_phone', '')}"
        ),
        fontsize=7.5,
        color=color,
    )

    handwritten(
        page_2,
        62,
        146,
        case.get("application_date"),
        9,
    )
    handwritten(
        page_2,
        430,
        146,
        case.get("student_signature"),
        9,
    )
    handwritten(
        page_2,
        58,
        245,
        case.get("manager_name"),
        9,
    )

    add_textbox(
        page_2,
        (55, 285, 560, 395),
        case.get("manager_comments"),
        fontsize=8.2,
        color=color,
    )

    handwritten(
        page_2,
        62,
        430,
        case.get("application_date"),
        9,
    )
    handwritten(
        page_2,
        430,
        430,
        case.get("manager_signature"),
        9,
    )

    handwritten(
        page_3,
        185,
        224,
        case.get("field_of_study"),
        9,
    )
    handwritten(
        page_3,
        470,
        224,
        case.get("cycle_of_study"),
        9,
    )
    handwritten(
        page_3,
        60,
        305,
        case.get("application_date"),
        9,
    )
    handwritten(
        page_3,
        430,
        305,
        case.get("student_signature"),
        9,
    )

    document.save(
        output_path,
        garbage=4,
        deflate=True,
    )
    document.close()


def generate_application_pdf(
    case: dict[str, Any],
    template_path: Path,
    output_path: Path,
) -> None:
    category = case.get("primary_category", "valid")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if category == "broken":
        create_broken_pdf(
            case,
            template_path,
            output_path,
        )

    elif category == "handwritten":
        create_handwritten_pdf(
            case,
            template_path,
            output_path,
        )

    else:
        create_normal_pdf(
            case,
            template_path,
            output_path,
        )
