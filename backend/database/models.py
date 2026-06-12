from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.db import Base

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(100), unique=True, index=True, nullable=False)

    status = Column(String(100), nullable=True)

    email_sender = Column(String(255), nullable=True)
    email_subject = Column(String(255), nullable=True)

    student_name = Column(String(255), nullable=True)
    student_id = Column(String(100), nullable=True)
    student_email = Column(String(255), nullable=True)

    company_name = Column(String(255), nullable=True)
    supervisor_name = Column(String(255), nullable=True)
    supervisor_email = Column(String(255), nullable=True)

    internship_start_date = Column(String(50), nullable=True)
    internship_end_date = Column(String(50), nullable=True)

    recommendation = Column(String(100), nullable=True)
    recommendation_reason = Column(Text, nullable=True)

    next_action = Column(String(100), nullable=True)

    final_decision = Column(String(100), nullable=True)
    final_decision_by = Column(String(255), nullable=True)
    final_decision_note = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    audit_logs = relationship(
        "AuditLog",
        back_populates="case",
        cascade="all, delete-orphan"
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    case_id = Column(
        String(100),
        ForeignKey("cases.case_id"),
        nullable=False
    )

    agent_name = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="audit_logs")
