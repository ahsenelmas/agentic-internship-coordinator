from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_non_existing_case_audit_logs():
    response = client.get("/cases/non-existing-case-id/audit-logs")

    assert response.status_code in [200, 404]


def test_approve_non_existing_case():
    response = client.post(
        "/cases/non-existing-case-id/approve",
        json={
            "decision_by": "Test Coordinator",
            "note": "Testing invalid case ID."
        }
    )

    assert response.status_code in [400, 404, 422]


def test_reject_non_existing_case():
    response = client.post(
        "/cases/non-existing-case-id/reject",
        json={
            "decision_by": "Test Coordinator",
            "note": "Testing invalid case ID."
        }
    )

    assert response.status_code in [400, 404, 422]


def test_request_clarification_non_existing_case():
    response = client.post(
        "/cases/non-existing-case-id/request-clarification",
        json={
            "decision_by": "Test Coordinator",
            "note": "Testing invalid case ID."
        }
    )

    assert response.status_code in [400, 404, 422]
