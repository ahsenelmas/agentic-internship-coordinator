from typing import List, Optional, TypedDict


class InternshipCaseState(TypedDict, total=False):
    # Basic case information
    case_id: str
    status: str

    # Email information
    email_sender: str
    email_subject: str
    email_body: str
    attachment_paths: List[str]

    # Extracted student information
    student_name: Optional[str]
    student_id: Optional[str]
    student_email: Optional[str]
    student_signature: Optional[str]

    # Extracted company information
    company_name: Optional[str]
    company_address: Optional[str]
    company_country: Optional[str]

    # Extracted supervisor information
    supervisor_name: Optional[str]
    supervisor_email: Optional[str]

    # Extracted internship information
    internship_start_date: Optional[str]
    internship_end_date: Optional[str]
    weekly_hours: Optional[str]

    # Extraction and security analysis
    extraction_warnings: List[str]
    security_flag: bool
    security_reasons: List[str]

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

    # Generated messages
    clarification_email_subject: Optional[str]
    clarification_email_body: Optional[str]

    supervisor_email_subject: Optional[str]
    supervisor_email_body: Optional[str]

    coordinator_notification_subject: Optional[str]
    coordinator_notification_body: Optional[str]

    # Audit trail
    audit_log: List[str]
