from datetime import datetime

from models.case_state import InternshipCaseState
from validation.completeness_rules import (
    check_completeness,
)


def completeness_validation_agent(
    state: InternshipCaseState,
) -> InternshipCaseState:
    """
    Validate that all required application fields are present.

    Existing clarification flags from document-quality,
    security, or consistency analysis must be preserved.
    """

    result = check_completeness(state) # type: ignore

    missing_fields = result["missing_fields"]
    state["missing_fields"] = missing_fields

    previous_clarification = bool(
        state.get(
            "clarification_needed",
            False,
        )
    )

    state["clarification_needed"] = (
        previous_clarification
        or not result["complete"]
    )

    if missing_fields:
        state["status"] = "APPLICATION_INCOMPLETE"

        message = (
            "Missing fields: "
            + ", ".join(missing_fields)
        )

    elif state["clarification_needed"]:
        state["status"] = "CLARIFICATION_REQUIRED"

        message = (
            "All required fields are present, but "
            "additional clarification is required."
        )

    else:
        state["status"] = "APPLICATION_COMPLETE"
        message = "All required fields are present."

    state.setdefault(
        "audit_log",
        [],
    ).append(
        f"[{datetime.now()}] "
        f"Completeness Validation Agent: {message}"
    )

    return state
