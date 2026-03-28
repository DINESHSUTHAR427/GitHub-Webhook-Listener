import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import hmac
import hashlib
import json

GITHUB_SECRET = "test_secret"


def create_signature(payload: bytes) -> str:
    return "sha256=" + hmac.new(
        GITHUB_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()


@pytest.fixture
def mock_db():
    with patch('app.database.connection.engine') as mock_engine:
        mock_session = MagicMock()
        with patch('app.database.connection.SessionLocal', return_value=mock_session):
            yield mock_session


@pytest.fixture
def client(mock_db):
    with patch.dict('os.environ', {'GITHUB_WEBHOOK_SECRET': GITHUB_SECRET}):
        from app.main import app
        
        def override_get_db():
            try:
                yield mock_db
            finally:
                pass
        
        from app.database import get_db
        app.dependency_overrides[get_db] = override_get_db
        
        with TestClient(app) as test_client:
            yield test_client
        
        app.dependency_overrides.clear()


def test_health_check(client):
    response = client.get("/webhook/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_missing_event_header(client):
    response = client.post(
        "/webhook/github",
        json={"test": "data"}
    )
    assert response.status_code == 400
    assert "X-GitHub-Event" in response.json()["detail"]


def test_missing_delivery_header(client):
    response = client.post(
        "/webhook/github",
        json={"test": "data"},
        headers={"X-GitHub-Event": "push"}
    )
    assert response.status_code == 400
    assert "X-GitHub-Delivery" in response.json()["detail"]


def test_invalid_signature(client):
    payload = json.dumps({"test": "data"}).encode()
    response = client.post(
        "/webhook/github",
        content=payload,
        headers={
            "X-GitHub-Event": "push",
            "X-GitHub-Delivery": "test-delivery-id",
            "X-Hub-Signature-256": "sha256=invalidsignature"
        }
    )
    assert response.status_code == 401
