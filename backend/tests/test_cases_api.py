from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_cases_endpoint():
    response = client.get("/cases")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
