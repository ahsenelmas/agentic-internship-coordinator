from typing import TypedDict, List, Optional


class InternshipCaseState(TypedDict, total=False):
    # Basic case information
    case_id: str
    status: str

    # Email information
    email_sender: str
    email_subject: str
    email_body: str
    attachment_paths: List[str]

    # Extracted student/company information
    student_name: Optional[str]
    student_id: Optional[str]
    student_email: Optional[str]
    company_name: Optional[str]
    supervisor_name: Optional[str]
    supervisor_email: Optional[str]
    internship_start_date: Optional[str]
    internship_end_date: Optional[str]

    # Validation results
    missing_fields: List[str]
    rule_violations: List[str]

    # Workflow flags
    clarification_needed: bool
    supervisor_verification_needed: bool

    # Final recommendation
    recommendation: Optional[str]
    recommendation_reason: Optional[str]

    next_action: Optional[str]

    clarification_email_subject: Optional[str]
    clarification_email_body: Optional[str]

    supervisor_email_subject: Optional[str]
    supervisor_email_body: Optional[str]

    coordinator_notification_subject: Optional[str]
    coordinator_notification_body: Optional[str]

    # Audit trail
    audit_log: List[str]
