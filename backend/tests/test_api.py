from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.main.handle_message", return_value="Mocked reply")
def test_chat_returns_200(mock_handle):
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json()["reply"] == "Mocked reply"


@patch("app.main.handle_message", return_value="Top suppliers are X, Y.")
def test_chat_calls_agent(mock_handle):
    response = client.post("/chat", json={"message": "top suppliers"})
    mock_handle.assert_called_once_with("top suppliers")


def test_chat_rejects_missing_message():
    response = client.post("/chat", json={})
    assert response.status_code == 422


def test_chat_rejects_wrong_type():
    response = client.post("/chat", json={"message": 123})
    assert response.status_code == 422
