import uuid
from datetime import datetime
from models.case_state import InternshipCaseState


def email_intake_agent(state: InternshipCaseState) -> InternshipCaseState:
    """
    Agent 1: Email Intake Agent

    Purpose:
    - Create a case ID if missing
    - Set first status
    - Store basic email information
    - Add audit log
    """

    if not state.get("case_id"):
        state["case_id"] = f"CASE-{uuid.uuid4().hex[:8].upper()}"

    state["status"] = "EMAIL_RECEIVED"

    if "audit_log" not in state:
        state["audit_log"] = []

    state["audit_log"].append(
        f"[{datetime.now()}] Email Intake Agent: Email received from {state.get('email_sender')}"
    )

    return state
