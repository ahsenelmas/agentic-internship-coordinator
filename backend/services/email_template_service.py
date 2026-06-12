def build_clarification_email(state: dict) -> dict:
    missing_fields = state.get("missing_fields", [])
    student_name = state.get("student_name") or "Student"
    case_id = state.get("case_id")

    missing_text = ", ".join(missing_fields)

    subject = f"Clarification Required for Internship Application - {case_id}"

    body = (
        f"Dear {student_name},\n\n"
        f"Thank you for submitting your internship application.\n\n"
        f"After reviewing your documents, we found that the following information is missing:\n"
        f"{missing_text}\n\n"
        f"Please send the missing information or corrected document so that your application can be processed.\n\n"
        f"Case ID: {case_id}\n\n"
        f"Best regards,\n"
        f"Internship Coordination Office"
    )

    return {
        "subject": subject,
        "body": body
    }


def build_supervisor_verification_email(state: dict) -> dict:
    supervisor_name = state.get("supervisor_name") or "Supervisor"
    student_name = state.get("student_name") or "the student"
    company_name = state.get("company_name") or "your company"
    case_id = state.get("case_id")

    subject = f"Internship Verification Request - {case_id}"

    body = (
        f"Dear {supervisor_name},\n\n"
        f"We are contacting you regarding the internship application of {student_name} at {company_name}.\n\n"
        f"Could you please confirm that your company accepts this student for the internship and that the provided internship details are correct?\n\n"
        f"Case ID: {case_id}\n\n"
        f"Best regards,\n"
        f"Internship Coordination Office"
    )

    return {
        "subject": subject,
        "body": body
    }


def build_coordinator_notification(state: dict) -> dict:
    case_id = state.get("case_id")
    student_name = state.get("student_name") or "Unknown student"
    company_name = state.get("company_name") or "Unknown company"
    recommendation = state.get("recommendation")
    reason = state.get("recommendation_reason")

    subject = f"Internship Application Review Ready - {case_id}"

    body = (
        f"A new internship application has been processed.\n\n"
        f"Case ID: {case_id}\n"
        f"Student: {student_name}\n"
        f"Company: {company_name}\n"
        f"Recommendation: {recommendation}\n\n"
        f"Reason:\n{reason}\n\n"
        f"Please review the case and make the final decision."
    )

    return {
        "subject": subject,
        "body": body
    }
