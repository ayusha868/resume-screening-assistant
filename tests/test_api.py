import io
import uuid

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from app.main import app

client = TestClient(app)


def _make_test_pdf(text: str) -> bytes:
    """Generates a tiny real PDF in memory so tests don't need a sample file on disk."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 700, text)
    c.save()
    buffer.seek(0)
    return buffer.read()


def _register_and_login():
    email = f"{uuid.uuid4()}@example.com"
    password = "testpassword123"

    register_response = client.post(
        "/auth/register", json={"email": email, "password": password}
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login():
    headers = _register_and_login()
    assert "Authorization" in headers


def test_login_with_wrong_password_fails():
    email = f"{uuid.uuid4()}@example.com"
    client.post("/auth/register", json={"email": email, "password": "correctpass"})

    response = client.post(
        "/auth/login", data={"username": email, "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_upload_resume_and_create_job_and_match():
    headers = _register_and_login()

    pdf_bytes = _make_test_pdf("Experienced Python developer skilled in FastAPI, Docker, and SQL.")
    resume_response = client.post(
        "/resumes/upload",
        headers=headers,
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert resume_response.status_code == 201
    resume_id = resume_response.json()["id"]
    assert "Python" in resume_response.json()["raw_text"]

    job_response = client.post(
        "/jobs",
        headers=headers,
        json={
            "title": "Backend Engineer",
            "description": "Looking for a backend engineer with Python and Docker experience.",
            "required_skills": ["Python", "Docker", "Kubernetes"],
        },
    )
    assert job_response.status_code == 201
    job_id = job_response.json()["id"]

    match_response = client.post(
        "/match",
        headers=headers,
        json={"resume_id": resume_id, "job_id": job_id},
    )
    assert match_response.status_code == 201
    body = match_response.json()
    assert 0 <= body["score"] <= 100
    assert "Python" in body["matched_skills"]
    assert "Kubernetes" in body["missing_skills"]


def test_dashboard_returns_counts():
    headers = _register_and_login()

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert "resumes_uploaded" in body
    assert "jobs_created" in body
    assert "average_match_score" in body


def test_protected_route_requires_auth():
    response = client.get("/resumes")
    assert response.status_code == 401