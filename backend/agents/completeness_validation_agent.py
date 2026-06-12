from datetime import datetime
from models.case_state import InternshipCaseState
from validation.completeness_rules import check_completeness


def completeness_validation_agent(state: InternshipCaseState) -> InternshipCaseState:
    """
    Agent 3: Completeness Validation Agent

    Purpose:
    - Check whether all required information exists
    - Decide if clarification is needed
    """

    result = check_completeness(state)

    state["missing_fields"] = result["missing_fields"]
    state["clarification_needed"] = not result["complete"]

    if result["complete"]:
        state["status"] = "COMPLETE"
        message = "All required fields are present."
    else:
        state["status"] = "INCOMPLETE"
        message = f"Missing fields: {', '.join(result['missing_fields'])}"

    state.setdefault("audit_log", []).append(
        f"[{datetime.now()}] Completeness Validation Agent: {message}"
    )

    return state
