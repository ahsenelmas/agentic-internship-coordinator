from datetime import datetime
from models.case_state import InternshipCaseState


PERSONAL_EMAIL_DOMAINS = [
    "@gmail.com",
    "@yahoo.com",
    "@hotmail.com",
    "@outlook.com"
]


def is_personal_email(email: str) -> bool:
    email = email.lower().strip()
    return any(email.endswith(domain) for domain in PERSONAL_EMAIL_DOMAINS)


def supervisor_verification_agent(state: InternshipCaseState) -> InternshipCaseState:
    """
    Agent 5: Supervisor Verification Agent

    Purpose:
    - Decide if company supervisor verification is required
    - Personal email domains require additional verification
    - Professional company emails can continue without extra verification
    """

    supervisor_email = state.get("supervisor_email")
    company_name = state.get("company_name")

    verification_required = False
    reason = ""

    if not supervisor_email:
        verification_required = False
        reason = "Supervisor email is missing, so student clarification is needed first."

    elif is_personal_email(supervisor_email):
        verification_required = True
        reason = "Supervisor email uses a personal email domain, so verification is required."

    elif company_name and supervisor_email:
        verification_required = False
        reason = "Supervisor email appears to be professional. No extra verification required."

    else:
        verification_required = True
        reason = "Company or supervisor information is unclear, so verification is required."

    state["supervisor_verification_needed"] = verification_required

    if verification_required:
        state["status"] = "SUPERVISOR_VERIFICATION_REQUIRED"
    else:
        state["status"] = "SUPERVISOR_VERIFICATION_NOT_REQUIRED"

    state.setdefault("audit_log", []).append(
        f"[{datetime.now()}] Supervisor Verification Agent: {reason}"
    )

    return state
