from pathlib import Path


# Folder containing this file
BASE_DIR = Path(__file__).resolve().parent

# Main project folder
PROJECT_ROOT = BASE_DIR.parent.parent

# ATA PDF template
TEMPLATE_PATH = BASE_DIR / "template" / "sample_anonymous_workplace.pdf"

# Generated files will be created here
OUTPUT_DIR = PROJECT_ROOT / "generated_test_dataset"

# Category distribution
CATEGORY_COUNTS = {
    "malicious": 10,
    "broken": 10,
    "handwritten": 10,
    "missing_crucial_information": 10,
    "requires_clarification": 20,
    "school_requirement_rejection": 10,
    "valid": 30,
}


def create_output_directory() -> None:
    """Create the output folder if it does not exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
