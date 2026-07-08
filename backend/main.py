import os
import shutil
import uuid

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from security.auth import verify_api_key

from graph.internship_graph import build_internship_graph

from database.db import Base, engine, get_db
from database.crud import (
    save_case_result,
    save_audit_logs,
    get_all_cases,
    get_case_by_case_id,
    get_audit_logs_by_case_id,
    update_final_decision
)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Agentic Internship Coordinator API",
    description="LangGraph-based agentic system for internship application processing",
    version="1.0.0"
)


# =========================================================
# LANGGRAPH WORKFLOW
# =========================================================

internship_graph = build_internship_graph()


# =========================================================
# FILE UPLOAD CONFIGURATION
# =========================================================

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================================================
# LANGSMITH OBSERVABILITY CONFIGURATION
# =========================================================

def get_langsmith_config(
    run_name: str,
    initial_state: dict,
    source: str
):
    """
    Creates tracing configuration for LangSmith.

    This config is passed into LangGraph invoke().
    It helps us trace each internship application processing run
    and identify where the request came from.
    """

    return {
        "run_name": run_name,
        "tags": [
            os.getenv("APP_ENV", "local"),
            "agentic-internship-coordinator",
            "langgraph",
            source
        ],
        "metadata": {
            "source": source,
            "email_sender": initial_state.get("email_sender"),
            "email_subject": initial_state.get("email_subject"),
            "has_attachments": bool(initial_state.get("attachment_paths")),
        },
    }


# =========================================================
# REQUEST MODELS
# =========================================================

class IntakeRequest(BaseModel):
    email_sender: str
    email_subject: str
    email_body: str
    attachment_paths: Optional[List[str]] = []


class FinalDecisionRequest(BaseModel):
    decision_by: str
    note: Optional[str] = ""


# =========================================================
# BASIC ROUTES
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Agentic Internship Coordinator API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# =========================================================
# CASE INTAKE ROUTE - JSON BODY
# =========================================================

@app.post("/cases/intake")
def intake_case(
    request: IntakeRequest,
    db: Session = Depends(get_db)
):
    initial_state = {
        "email_sender": request.email_sender,
        "email_subject": request.email_subject,
        "email_body": request.email_body,
        "attachment_paths": request.attachment_paths,
        "missing_fields": [],
        "rule_violations": [],
        "clarification_needed": False,
        "supervisor_verification_needed": False,
        "audit_log": []
    }

    result = internship_graph.invoke(
        initial_state,  # type: ignore
        config=get_langsmith_config(
            run_name="internship_case_intake",
            initial_state=initial_state,
            source="fastapi_json_intake",
        ), # type: ignore
    )

    saved_case = save_case_result(db, result)
    save_audit_logs(db, result["case_id"], result.get("audit_log", []))

    result["database_id"] = saved_case.id

    return result


# =========================================================
# CASE UPLOAD ROUTE - PDF FILE
# =========================================================

@app.post("/cases/upload")
def upload_case(
    email_sender: str = Form(...),
    email_subject: str = Form(...),
    email_body: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_api_key)
):
    """
    Receives a real PDF file, saves it, processes it with LangGraph,
    saves the result to PostgreSQL, and returns the recommendation.
    """

    if not file.filename.lower().endswith(".pdf"):  # type: ignore
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    initial_state = {
        "email_sender": email_sender,
        "email_subject": email_subject,
        "email_body": email_body,
        "attachment_paths": [file_path],
        "missing_fields": [],
        "rule_violations": [],
        "clarification_needed": False,
        "supervisor_verification_needed": False,
        "audit_log": []
    }

    result = internship_graph.invoke(
        initial_state, # type: ignore
        config=get_langsmith_config(
            run_name="internship_case_pdf_upload",
            initial_state=initial_state,
            source="fastapi_pdf_upload",
        ), # type: ignore
    )

    saved_case = save_case_result(db, result)
    save_audit_logs(db, result["case_id"], result.get("audit_log", []))

    result["database_id"] = saved_case.id
    result["uploaded_file_path"] = file_path

    return result


# =========================================================
# CASE LISTING AND DETAILS
# =========================================================

@app.get("/cases")
def list_cases(db: Session = Depends(get_db)):
    cases = get_all_cases(db)

    return cases


@app.get("/cases/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = get_case_by_case_id(db, case_id)

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return case


@app.get("/cases/{case_id}/audit-logs")
def get_case_audit_logs(case_id: str, db: Session = Depends(get_db)):
    case = get_case_by_case_id(db, case_id)

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    logs = get_audit_logs_by_case_id(db, case_id)

    return logs


# =========================================================
# HUMAN FINAL DECISION ROUTES
# =========================================================

@app.post("/cases/{case_id}/approve")
def approve_case(
    case_id: str,
    request: FinalDecisionRequest,
    db: Session = Depends(get_db)
):
    case = update_final_decision(
        db=db,
        case_id=case_id,
        final_decision="APPROVED",
        decision_by=request.decision_by,
        note=request.note  # type: ignore
    )

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return {
        "message": "Case approved by coordinator.",
        "case_id": case.case_id,
        "final_decision": case.final_decision,
        "final_decision_by": case.final_decision_by,
        "final_decision_note": case.final_decision_note,
        "status": case.status
    }


@app.post("/cases/{case_id}/reject")
def reject_case(
    case_id: str,
    request: FinalDecisionRequest,
    db: Session = Depends(get_db)
):
    case = update_final_decision(
        db=db,
        case_id=case_id,
        final_decision="REJECTED",
        decision_by=request.decision_by,
        note=request.note  # type: ignore
    )

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return {
        "message": "Case rejected by coordinator.",
        "case_id": case.case_id,
        "final_decision": case.final_decision,
        "final_decision_by": case.final_decision_by,
        "final_decision_note": case.final_decision_note,
        "status": case.status
    }


@app.post("/cases/{case_id}/request-clarification")
def request_clarification_case(
    case_id: str,
    request: FinalDecisionRequest,
    db: Session = Depends(get_db)
):
    case = update_final_decision(
        db=db,
        case_id=case_id,
        final_decision="CLARIFICATION_REQUESTED",
        decision_by=request.decision_by,
        note=request.note  # type: ignore
    )

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return {
        "message": "Clarification requested by coordinator.",
        "case_id": case.case_id,
        "final_decision": case.final_decision,
        "final_decision_by": case.final_decision_by,
        "final_decision_note": case.final_decision_note,
        "status": case.status
    }
