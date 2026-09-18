from datetime import datetime

from models.case_state import InternshipCaseState
from services.email_template_service import (
    build_clarification_email,
    build_coordinator_notification,
    build_supervisor_verification_email,
)


def _set_quality_clarification_email(
    state: InternshipCaseState,
    issues: list[str],
) -> None:
    student_name = (
        state.get("student_name")
        or "Student"
    )

    case_id = (
        state.get("case_id")
        or "unknown"
    )

    issue_list = "\n".join(
        f"- {issue}"
        for issue in issues
    )

    state["clarification_email_subject"] = (
        "Clarification Required for "
        f"Internship Application - {case_id}"
    )

    state["clarification_email_body"] = (
        f"Dear {student_name},\n\n"
        "Thank you for submitting your "
        "internship application.\n\n"
        "We need clarification regarding "
        "the following points:\n"
        f"{issue_list}\n\n"
        "Please provide corrected or additional "
        "information so that your application "
        "can be processed.\n\n"
        f"Case ID: {case_id}\n\n"
        "Best regards,\n"
        "Internship Coordination Office"
    )


def decision_recommendation_agent(
    state: InternshipCaseState,
) -> InternshipCaseState:
    """
    Generate a recommendation for the human coordinator.

    Priority:
    1. Security concern
    2. Missing required fields
    3. Other clarification requirement
    4. University-rule rejection
    5. Supervisor verification
    6. Approval
    """

    missing_fields = state.get(
        "missing_fields",
        [],
    )

    rule_violations = state.get(
        "rule_violations",
        [],
    )

    security_flag = bool(
        state.get(
            "security_flag",
            False,
        )
    )

    security_reasons = state.get(
        "security_reasons",
        [],
    )

    extraction_warnings = state.get(
        "extraction_warnings",
        [],
    )

    clarification_needed = bool(
        state.get(
            "clarification_needed",
            False,
        )
    )

    supervisor_verification_needed = bool(
        state.get(
            "supervisor_verification_needed",
            False,
        )
    )

    if security_flag:
        state["recommendation"] = (
            "REQUEST_CLARIFICATION"
        )

        reasons = security_reasons or [
            "The application requires a "
            "security review."
        ]

        state["recommendation_reason"] = (
            "Potentially unsafe or manipulative "
            "content was detected: "
            + " ".join(reasons)
        )

        state["next_action"] = (
            "COORDINATOR_SECURITY_REVIEW"
        )

        coordinator_email = (
            build_coordinator_notification(
                state
            )
        )

        state[
            "coordinator_notification_subject"
        ] = coordinator_email["subject"]

        state[
            "coordinator_notification_body"
        ] = coordinator_email["body"]

    elif missing_fields:
        state["recommendation"] = (
            "REQUEST_CLARIFICATION"
        )

        state["recommendation_reason"] = (
            "Application is incomplete. "
            "Missing fields: "
            + ", ".join(missing_fields)
        )

        state["next_action"] = (
            "SEND_CLARIFICATION_EMAIL"
        )

        clarification_email = (
            build_clarification_email(
                state
            )
        )

        state[
            "clarification_email_subject"
        ] = clarification_email["subject"]

        state[
            "clarification_email_body"
        ] = clarification_email["body"]

    elif clarification_needed:
        state["recommendation"] = (
            "REQUEST_CLARIFICATION"
        )

        issues = extraction_warnings or [
            "The submitted information "
            "requires clarification."
        ]

        state["recommendation_reason"] = (
            "Application requires clarification: "
            + " ".join(issues)
        )

        state["next_action"] = (
            "SEND_CLARIFICATION_EMAIL"
        )

        _set_quality_clarification_email(
            state,
            issues,
        )

    elif rule_violations:
        state["recommendation"] = "REJECT"

        state["recommendation_reason"] = (
            "Application violates university "
            "requirements: "
            + " ".join(rule_violations)
        )

        state["next_action"] = (
            "COORDINATOR_REVIEW"
        )

        coordinator_email = (
            build_coordinator_notification(
                state
            )
        )

        state[
            "coordinator_notification_subject"
        ] = coordinator_email["subject"]

        state[
            "coordinator_notification_body"
        ] = coordinator_email["body"]

    elif supervisor_verification_needed:
        state["recommendation"] = (
            "WAIT_FOR_SUPERVISOR_RESPONSE"
        )

        state["recommendation_reason"] = (
            "Supervisor verification is required "
            "before final decision."
        )

        state["next_action"] = (
            "SEND_SUPERVISOR_VERIFICATION_EMAIL"
        )

        supervisor_email = (
            build_supervisor_verification_email(
                state
            )
        )

        state[
            "supervisor_email_subject"
        ] = supervisor_email["subject"]

        state[
            "supervisor_email_body"
        ] = supervisor_email["body"]

    else:
        state["recommendation"] = "APPROVE"

        state["recommendation_reason"] = (
            "Application is complete and follows "
            "university rules."
        )

        state["next_action"] = (
            "COORDINATOR_APPROVAL"
        )

        coordinator_email = (
            build_coordinator_notification(
                state
            )
        )

        state[
            "coordinator_notification_subject"
        ] = coordinator_email["subject"]

        state[
            "coordinator_notification_body"
        ] = coordinator_email["body"]

    state["status"] = "RECOMMENDATION_READY"

    state.setdefault(
        "audit_log",
        [],
    ).append(
        f"[{datetime.now()}] "
        "Decision Recommendation Agent: "
        f"{state['recommendation']} - "
        f"{state['recommendation_reason']}"
    )

    return state
