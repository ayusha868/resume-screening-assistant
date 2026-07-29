from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, resumes, jobs, match, dashboard

# Creates all tables defined in app/models.py if they don't exist yet.
# Fine for a project this size — a real production app would use Alembic migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Screening Assistant", version="0.1.0")

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(match.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Resume Screening Assistant API is running"}