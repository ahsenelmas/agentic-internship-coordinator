from agents.document_extraction_agent import document_extraction_agent
from models.case_state import InternshipCaseState

test_state: InternshipCaseState = {
    "case_id": "CASE-TEST-002",
    "status": "EMAIL_RECEIVED",
    "email_sender": "student@example.com",
    "email_subject": "Internship Application",
    "email_body": "Dear Coordinator, please find attached.",
    "attachment_paths": ["sample_files/sample_application.pdf"],
    "audit_log": []
}

result = document_extraction_agent(test_state)

print(result)
