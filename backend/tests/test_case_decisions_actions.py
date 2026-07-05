from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def get_first_case_id():
    response = client.get("/cases")
    assert response.status_code == 200

    cases = response.json()

    if not cases:
        return None

    return cases[0]["case_id"]


def test_approve_case_endpoint():
    case_id = get_first_case_id()

    if case_id is None:
        return

    response = client.post(
        f"/cases/{case_id}/approve",
        json={
            "decision_by": "Test Coordinator",
            "note": "Approved during automated testing."
        }
    )

    assert response.status_code in [200, 201]
    assert "message" in response.json()


def test_reject_case_endpoint():
    case_id = get_first_case_id()

    if case_id is None:
        return

    response = client.post(
        f"/cases/{case_id}/reject",
        json={
            "decision_by": "Test Coordinator",
            "note": "Rejected during automated testing."
        }
    )

    assert response.status_code in [200, 201]
    assert "message" in response.json()


def test_request_clarification_endpoint():
    case_id = get_first_case_id()

    if case_id is None:
        return

    response = client.post(
        f"/cases/{case_id}/request-clarification",
        json={
            "decision_by": "Test Coordinator",
            "note": "Clarification requested during automated testing."
        }
    )

    assert response.status_code in [200, 201]
    assert "message" in response.json()
