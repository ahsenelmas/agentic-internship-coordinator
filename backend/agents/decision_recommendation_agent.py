from datetime import datetime
from models.case_state import InternshipCaseState
from services.email_template_service import (
    build_clarification_email,
    build_supervisor_verification_email,
    build_coordinator_notification
)


def decision_recommendation_agent(state: InternshipCaseState) -> InternshipCaseState:
    """
    Agent 6: Decision Recommendation Agent

    Purpose:
    - Generate recommendation for human coordinator
    - Does not make final decision automatically
    - Adds next_action for n8n routing
    - Adds email draft fields for n8n email sending
    """

    missing_fields = state.get("missing_fields", [])
    rule_violations = state.get("rule_violations", [])
    supervisor_verification_needed = state.get("supervisor_verification_needed", False)

    if missing_fields:
        state["recommendation"] = "REQUEST_CLARIFICATION"
        state["recommendation_reason"] = (
            "Application is incomplete. Missing fields: "
            + ", ".join(missing_fields)
        )
        state["next_action"] = "SEND_CLARIFICATION_EMAIL"

        clarification_email = build_clarification_email(state)
        state["clarification_email_subject"] = clarification_email["subject"]
        state["clarification_email_body"] = clarification_email["body"]

    elif rule_violations:
        state["recommendation"] = "REJECT_OR_CLARIFY"
        state["recommendation_reason"] = (
            "Application has university rule violations: "
            + ", ".join(rule_violations)
        )
        state["next_action"] = "COORDINATOR_REVIEW"

        coordinator_email = build_coordinator_notification(state)
        state["coordinator_notification_subject"] = coordinator_email["subject"]
        state["coordinator_notification_body"] = coordinator_email["body"]

    elif supervisor_verification_needed:
        state["recommendation"] = "WAIT_FOR_SUPERVISOR_RESPONSE"
        state["recommendation_reason"] = (
            "Supervisor verification is required before final decision."
        )
        state["next_action"] = "SEND_SUPERVISOR_VERIFICATION_EMAIL"

        supervisor_email = build_supervisor_verification_email(state)
        state["supervisor_email_subject"] = supervisor_email["subject"]
        state["supervisor_email_body"] = supervisor_email["body"]

    else:
        state["recommendation"] = "APPROVE"
        state["recommendation_reason"] = (
            "Application is complete and follows university rules."
        )
        state["next_action"] = "COORDINATOR_APPROVAL"

        coordinator_email = build_coordinator_notification(state)
        state["coordinator_notification_subject"] = coordinator_email["subject"]
        state["coordinator_notification_body"] = coordinator_email["body"]

    state["status"] = "RECOMMENDATION_READY"

    state.setdefault("audit_log", []).append(
        f"[{datetime.now()}] Decision Recommendation Agent: "
        f"{state['recommendation']} - {state['recommendation_reason']}"
    )

    return state
