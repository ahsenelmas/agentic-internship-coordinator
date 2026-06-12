from pathlib import Path
import fitz


SAMPLE_FILES = [
    "sample_application",
    "sample_incomplete_application",
    "sample_rule_violation_application",
    "sample_ambiguous_application",
]


def create_pdf_from_txt(file_stem: str):
    input_path = Path(f"sample_files/{file_stem}.txt")
    output_path = Path(f"sample_files/{file_stem}.pdf")

    if not input_path.exists():
        print(f"Missing file: {input_path}")
        return

    text = input_path.read_text(encoding="utf-8")

    doc = fitz.open()
    page = doc.new_page()

    page.insert_text(
        (72, 72),
        text,
        fontsize=12
    )

    doc.save(output_path)
    doc.close()

    print(f"PDF created successfully: {output_path}")


def create_all_sample_pdfs():
    for file_stem in SAMPLE_FILES:
        create_pdf_from_txt(file_stem)


if __name__ == "__main__":
    create_all_sample_pdfs()
