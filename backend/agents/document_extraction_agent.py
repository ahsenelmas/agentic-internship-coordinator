from datetime import datetime
from models.case_state import InternshipCaseState
from services.pdf_service import extract_text_from_pdf, find_value_after_label, extract_email


def document_extraction_agent(state: InternshipCaseState) -> InternshipCaseState:
    """
    Agent 2: Document Extraction Agent

    Purpose:
    - Read PDF attachment
    - Extract student/company/supervisor information
    - Add extracted fields to state
    """

    attachment_paths = state.get("attachment_paths", [])

    if not attachment_paths:
        state["status"] = "NO_ATTACHMENT_FOUND"
        state.setdefault("audit_log", []).append(
            f"[{datetime.now()}] Document Extraction Agent: No attachment found."
        )
        return state

    pdf_path = attachment_paths[0]
    text = extract_text_from_pdf(pdf_path)

    state["student_name"] = find_value_after_label(text, "Student Name")
    state["student_id"] = find_value_after_label(text, "Student ID")
    state["student_email"] = find_value_after_label(text, "Student Email")
    state["company_name"] = find_value_after_label(text, "Company Name")
    state["supervisor_name"] = find_value_after_label(text, "Supervisor Name")
    state["supervisor_email"] = find_value_after_label(text, "Supervisor Email")
    state["internship_start_date"] = find_value_after_label(text, "Internship Start Date")
    state["internship_end_date"] = find_value_after_label(text, "Internship End Date")

    state["status"] = "DOCUMENT_EXTRACTED"

    state.setdefault("audit_log", []).append(
        f"[{datetime.now()}] Document Extraction Agent: Extracted data from {pdf_path}."
    )

    return state
