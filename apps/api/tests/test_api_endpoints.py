import pytest
import os
import sys
from fastapi.testclient import TestClient

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'packages'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Correlation-Id" in response.headers


def test_openapi_docs():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Kindlepreneur API"
    # Core publishing endpoints
    assert "/api/v1/projects/" in schema["paths"]
    assert "/api/v1/artifacts/" in schema["paths"]
    assert "/api/v1/approvals/" in schema["paths"]
    assert "/api/v1/tasks/projects/{project_id}/tasks" in schema["paths"]
    assert "/api/v1/analytics/projects/{project_id}" in schema["paths"]
    # Phase 2 Marketplace Studio endpoints
    assert "/api/v1/marketplace/accounts" in schema["paths"]
    assert "/api/v1/marketplace/listings" in schema["paths"]
    assert "/api/v1/marketplace/preflight" in schema["paths"]
    assert "/api/v1/marketplace/publish" in schema["paths"]
    # Phase 2 AudienceOS endpoints
    assert "/api/v1/audience/sources" in schema["paths"]
    assert "/api/v1/audience/opportunities" in schema["paths"]
    assert "/api/v1/audience/drafts" in schema["paths"]
    assert "/api/v1/audience/subscribers" in schema["paths"]
    assert "/api/v1/audience/landing-pages" in schema["paths"]
    assert "/api/v1/audience/kill-switches" in schema["paths"]
