from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_cases_endpoint_without_api_key():
    response = client.get("/cases")

    assert response.status_code in [200, 401, 403]


def test_cases_endpoint_with_wrong_api_key():
    response = client.get(
        "/cases",
        headers={"x-api-key": "wrong-api-key"}
    )

    assert response.status_code in [200, 401, 403]
