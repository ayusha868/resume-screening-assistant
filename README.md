# Resume Screening Assistant (JobMatch AI)

An AI-powered backend API that matches resumes against job descriptions using
semantic similarity (embeddings) and skill extraction — built with FastAPI,
PostgreSQL, and a local sentence-transformer model.

Recruiters post jobs. Candidates upload resumes (PDF). The API extracts the
resume text, embeds both texts, computes a similarity score, and identifies
which required skills are present or missing — all behind JWT authentication.

## Features

- JWT authentication (register / login), passwords hashed with bcrypt
- Resume upload with automatic PDF text extraction (`pypdf`)
- Job posting creation
- AI-powered matching: cosine similarity on sentence embeddings + skill
  extraction, returning a score and matched/missing skills
- Dashboard endpoint: resumes uploaded, jobs created, average match score
- Auto-generated Swagger docs (`/docs`)
- Fully containerized with Docker Compose (API + Postgres, one command)
- Pytest test suite covering the full user flow

## Tech Stack

| Layer | Choice |
|---|---|
| API framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`, local, no API key) |
| PDF parsing | pypdf |
| Testing | Pytest + FastAPI TestClient |
| Containerization | Docker + Docker Compose |

## Architecture

```
Client (Swagger/Postman)
        │  HTTPS + JWT
        ▼
   FastAPI routers  (auth / resumes / jobs / match / dashboard)
        │
   AI layer (embeddings + skill extraction)
        │
   SQLAlchemy ORM
        │
   PostgreSQL
```

Routers handle HTTP only; they call into `app/ai.py` for the matching logic
and use SQLAlchemy models for persistence. See [`ARCHITECTURE.md`](./ARCHITECTURE.md)
for the full system design, database schema, and API design rationale.

## API Endpoints

| Method | Path | Auth required | Description |
|---|---|---|---|
| POST | `/auth/register` | no | Create an account |
| POST | `/auth/login` | no | Returns a JWT access token |
| POST | `/resumes/upload` | yes | Upload a PDF resume, extracts text |
| GET | `/resumes` | yes | List your own resumes |
| GET | `/resumes/{id}` | yes | Fetch one of your resumes |
| POST | `/jobs` | yes | Create a job posting |
| GET | `/jobs` | yes | List all job postings |
| GET | `/jobs/{id}` | yes | Fetch a job posting |
| POST | `/match` | yes | `{resume_id, job_id}` → score + matched/missing skills |
| GET | `/match/{id}` | yes | Fetch a previously computed match |
| GET | `/dashboard` | yes | Your resume/job counts + average match score |

Example `POST /match` response:
```json
{
  "id": 1,
  "resume_id": 3,
  "job_id": 2,
  "score": 92.4,
  "matched_skills": ["FastAPI", "Python", "SQL"],
  "missing_skills": ["Docker"],
  "created_at": "2026-07-29T12:00:00"
}
```

## Running Locally (without Docker)

```bash
# 1. Create and activate a virtual environment
uv venv
source .venv/bin/activate

# 2. Install dependencies
uv pip install -r requirements.txt

# 3. Start Postgres (if not already running)
docker run --name resume-screening-assistant-db \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=jobmatch \
  -p 5432:5432 -d postgres:16

# 4. Create a .env file
echo "DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/jobmatch" > .env
echo "JWT_SECRET=some-random-long-string-here" >> .env

# 5. Run the server
python -m uvicorn app.main:app --reload
```

Visit **http://127.0.0.1:8000/docs** for interactive Swagger docs.

## Running with Docker (one command)

```bash
docker compose up --build
```

This starts both the API and Postgres, wired together automatically. Visit
**http://127.0.0.1:8000/docs** once both containers report ready.

## Running Tests

```bash
python -m pytest -v
```

Tests spin up a FastAPI `TestClient` in-process and exercise the full flow:
register → login → upload resume → create job → match → dashboard, plus
auth-rejection cases. Requires Postgres to be reachable (either via Docker
Compose or the standalone container above).

## Project Structure

```
resume-screening-assistant/
├── app/
│   ├── main.py          # app entrypoint, router registration
│   ├── config.py        # environment-based settings
│   ├── database.py      # SQLAlchemy engine/session
│   ├── models.py         # User, Resume, Job, Match tables
│   ├── schemas.py        # Pydantic request/response models
│   ├── auth.py            # password hashing, JWT, get_current_user
│   ├── ai.py               # embeddings + skill extraction
│   └── routers/
│       ├── auth.py
│       ├── resumes.py
│       ├── jobs.py
│       ├── match.py
│       └── dashboard.py
├── tests/
│   └── test_api.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── ARCHITECTURE.md
└── README.md
```

## Design Notes

- **Layered design**: routers only handle HTTP; the AI/matching logic is
  isolated in `app/ai.py` behind plain functions, making it easy to swap the
  local embedding model for an API-based one (e.g. OpenAI embeddings) later.
- **Text extraction happens once**, at upload time, so repeated matches don't
  re-parse the PDF.
- **Tables are created via `Base.metadata.create_all()`** rather than Alembic
  migrations, a deliberate scope tradeoff for a project this size — Alembic
  would be the next step for a production version.
- **Skill taxonomy** (`app/ai.py`) is a simple curated list matched via regex;
  swappable for a proper NER model as a future improvement.

## Possible Next Steps

- Minimal frontend (upload form + results view)
- Role-based access control (recruiter vs. candidate)
- Alembic migrations
- Redis caching for repeated embedding lookups
- GitHub Actions CI running the test suite on push