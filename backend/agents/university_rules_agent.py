from datetime import datetime
from models.case_state import InternshipCaseState
from validation.university_rules import validate_university_rules


def university_rules_agent(state: InternshipCaseState) -> InternshipCaseState:
    """
    Agent 4: University Rules Agent

    Purpose:
    - Validate internship according to university rules
    """

    result = validate_university_rules(state)

    state["rule_violations"] = result["violations"]

    if result["valid"]:
        state["status"] = "RULES_VALID"
        message = "University rules are satisfied."
    else:
        state["status"] = "RULES_VIOLATED"
        message = f"Rule violations: {', '.join(result['violations'])}"

    state.setdefault("audit_log", []).append(
        f"[{datetime.now()}] University Rules Agent: {message}"
    )

    return state
