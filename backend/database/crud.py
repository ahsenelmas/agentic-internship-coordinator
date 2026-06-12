from sqlalchemy.orm import Session

from database.models import Case, AuditLog


def save_case_result(db: Session, result: dict) -> Case:
    """
    Saves processed LangGraph result into the cases table.
    """

    case = Case(
        case_id=result.get("case_id"),
        status=result.get("status"),

        email_sender=result.get("email_sender"),
        email_subject=result.get("email_subject"),

        student_name=result.get("student_name"),
        student_id=result.get("student_id"),
        student_email=result.get("student_email"),

        company_name=result.get("company_name"),
        supervisor_name=result.get("supervisor_name"),
        supervisor_email=result.get("supervisor_email"),

        internship_start_date=result.get("internship_start_date"),
        internship_end_date=result.get("internship_end_date"),

        recommendation=result.get("recommendation"),
        recommendation_reason=result.get("recommendation_reason"),

        next_action=result.get("next_action"),
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case


def save_audit_logs(db: Session, case_id: str, audit_logs: list) -> None:
    """
    Saves all audit log messages for one case.
    """

    for log_message in audit_logs:
        agent_name = extract_agent_name(log_message)

        audit_log = AuditLog(
            case_id=case_id,
            agent_name=agent_name,
            message=log_message
        )

        db.add(audit_log)

    db.commit()


def extract_agent_name(log_message: str) -> str:
    """
    Extracts agent name from log text.
    Example:
    [date] Email Intake Agent: message
    """

    try:
        after_bracket = log_message.split("] ", 1)[1]
        agent_name = after_bracket.split(":", 1)[0]
        return agent_name
    except Exception:
        return "Unknown Agent"


def get_all_cases(db: Session):
    return db.query(Case).order_by(Case.created_at.desc()).all()


def get_case_by_case_id(db: Session, case_id: str):
    return db.query(Case).filter(Case.case_id == case_id).first()


def get_audit_logs_by_case_id(db: Session, case_id: str):
    return (
        db.query(AuditLog)
        .filter(AuditLog.case_id == case_id)
        .order_by(AuditLog.created_at.asc())
        .all()
    )

def update_final_decision(
    db: Session,
    case_id: str,
    final_decision: str,
    decision_by: str,
    note: str = ""
):
    case = get_case_by_case_id(db, case_id)

    if not case:
        return None

    case.final_decision = final_decision
    case.final_decision_by = decision_by
    case.final_decision_note = note
    case.status = f"HUMAN_{final_decision}"

    db.commit()
    db.refresh(case)

    return case
