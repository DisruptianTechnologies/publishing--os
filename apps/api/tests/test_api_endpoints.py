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
    assert "/api/v1/analytics/usage" in schema["paths"]
    assert "/api/v1/analytics/audit-logs" in schema["paths"]
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
    # Phase 3 Production & Compilation endpoints
    assert "/api/v1/projects/{id}/compile" in schema["paths"]
    assert "/api/v1/projects/{id}/export/{format}" in schema["paths"]
    assert "/api/v1/projects/{id}/cover/dimensions" in schema["paths"]
    assert "/api/v1/projects/{id}/cover/prompt" in schema["paths"]
    assert "/api/v1/projects/{id}/chapters" in schema["paths"]
    assert "/api/v1/projects/{id}/chapters/{num}/assist" in schema["paths"]


def test_list_projects_endpoint():
    response = client.get("/api/v1/projects/")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) > 0
    first = json_data["data"][0]
    assert "id" in first
    assert "name" in first
    assert "project_type" in first


def test_get_project_by_id():
    response = client.get("/api/v1/projects/demo-project-001")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["id"] == "demo-project-001"
    assert "name" in json_data["data"]


def test_project_artifacts_and_stats():
    res_art = client.get("/api/v1/projects/demo-project-001/artifacts")
    assert res_art.status_code == 200
    assert len(res_art.json()["data"]) >= 1

    res_stats = client.get("/api/v1/projects/demo-project-001/stats")
    assert res_stats.status_code == 200
    stats = res_stats.json()["data"]
    assert "total_tokens" in stats
    assert "total_cost_usd" in stats


def test_approvals_workflow():
    res = client.get("/api/v1/approvals/")
    assert res.status_code == 200
    approvals = res.json()["data"]
    assert len(approvals) >= 1
    appr_id = approvals[0]["id"]

    res_single = client.get(f"/api/v1/approvals/{appr_id}")
    assert res_single.status_code == 200
    assert res_single.json()["data"]["id"] == appr_id

    res_approve = client.post(f"/api/v1/approvals/{appr_id}/approve", json={"reason": "QA Verified"})
    assert res_approve.status_code == 200
    assert res_approve.json()["data"]["success"] is True


def test_analytics_endpoints():
    res_proj = client.get("/api/v1/analytics/projects/demo-project-001")
    assert res_proj.status_code == 200
    assert res_proj.json()["data"]["project_id"] == "demo-project-001"

    res_usage = client.get("/api/v1/analytics/usage")
    assert res_usage.status_code == 200
    assert isinstance(res_usage.json()["data"], list)

    res_audit = client.get("/api/v1/analytics/audit-logs")
    assert res_audit.status_code == 200
    assert isinstance(res_audit.json()["data"], list)


def test_compilation_and_export_endpoints():
    # 1. Trigger compilation
    payload = {
        "title": "Granular QA Test Title",
        "author": "Test Author",
        "output_formats": ["epub", "pdf"],
        "trim_size": "6x9",
        "paper_type": "white"
    }
    res_compile = client.post("/api/v1/projects/demo-project-001/compile", json=payload)
    assert res_compile.status_code == 200
    result = res_compile.json()["data"]
    assert result["title"] == "Granular QA Test Title"
    assert len(result["compiled_artifacts"]) == 2

    # 2. Export EPUB binary stream
    res_epub = client.get("/api/v1/projects/demo-project-001/export/epub")
    assert res_epub.status_code == 200
    assert res_epub.headers["content-type"] == "application/epub+zip"
    assert res_epub.content[:2] == b"PK"  # Valid zip magic bytes

    # 3. Export PDF binary stream
    res_pdf = client.get("/api/v1/projects/demo-project-001/export/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert res_pdf.content.startswith(b"%PDF-1.4")


def test_cover_dimensions_endpoint():
    payload = {
        "page_count": 250,
        "trim_size": "6x9",
        "paper_type": "white"
    }
    res = client.post("/api/v1/projects/demo-project-001/cover/dimensions", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["page_count"] == 250
    assert data["spine_width_inches"] > 0.5
    assert data["can_print_spine_text"] is True
    assert data["dpi"] == 300


def test_writing_studio_chapter_assist_endpoints():
    # 1. List chapters
    res_ch = client.get("/api/v1/projects/demo-project-001/chapters")
    assert res_ch.status_code == 200
    chapters = res_ch.json()["data"]
    assert len(chapters) >= 1
    assert chapters[0]["chapter_number"] == 1

    # 2. Trope cleaner assist
    assist_payload = {
        "action": "polish_tropes",
        "text": "Furthermore, when we delve into the tapestry of human focus, it is important to note that."
    }
    res_assist = client.post("/api/v1/projects/demo-project-001/chapters/1/assist", json=assist_payload)
    assert res_assist.status_code == 200
    assist_data = res_assist.json()["data"]
    assert "delve into" not in assist_data["polished_text"]
    assert len(assist_data["tropes_removed"]) >= 3
