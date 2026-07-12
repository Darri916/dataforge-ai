import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_test_csv_path():
    """Points to a small sample CSV in the tests folder."""
    return os.path.join(os.path.dirname(__file__), "sample.csv")

def upload_sample_file():
    """Reusable upload step — returns file_id."""
    with open(get_test_csv_path(), "rb") as f:
        response = client.post("/api/upload/", files={"file": ("sample.csv", f, "text/csv")})
    assert response.status_code == 200
    return response.json()["file_id"]

# ─── Tests ────────────────────────────────────────────────────────────────────

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_upload_valid_csv():
    file_id = upload_sample_file()
    assert file_id is not None

def test_upload_invalid_file():
    response = client.post(
        "/api/upload/",
        files={"file": ("test.txt", b"not a csv", "text/plain")}
    )
    assert response.status_code == 400

def test_generate():
    file_id = upload_sample_file()
    response = client.post("/api/generate/", json={
        "file_id": file_id,
        "synthesizer": "gaussian_copula",
        "num_rows": 50,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["rows_generated"] == 50
    assert data["synthesizer_used"] == "gaussian_copula"

def test_quality():
    file_id = upload_sample_file()
    client.post("/api/generate/", json={
        "file_id": file_id,
        "synthesizer": "gaussian_copula",
        "num_rows": 50,
    })
    response = client.get(f"/api/quality/{file_id}")
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "column_metrics" in data

def test_privacy():
    file_id = upload_sample_file()
    client.post("/api/generate/", json={
        "file_id": file_id,
        "synthesizer": "gaussian_copula",
        "num_rows": 50,
    })
    response = client.get(f"/api/privacy/{file_id}")
    assert response.status_code == 200
    data = response.json()
    assert "overall_privacy_score" in data
    assert "reidentification_score" in data

def test_export_csv():
    file_id = upload_sample_file()
    client.post("/api/generate/", json={
        "file_id": file_id,
        "synthesizer": "gaussian_copula",
        "num_rows": 50,
    })
    response = client.get(f"/api/export/{file_id}/csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

def test_generate_file_not_found():
    response = client.post("/api/generate/", json={
        "file_id": "nonexistent-id",
        "synthesizer": "auto",
        "num_rows": 50,
    })
    assert response.status_code == 404