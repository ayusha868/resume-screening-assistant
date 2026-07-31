from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, resumes, jobs, match, dashboard

# Creates all tables defined in app/models.py if they don't exist yet.
# Fine for a project this size — a real production app would use Alembic migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Screening Assistant", version="0.1.0")

# Allows the frontend (served from a different origin, e.g. a local file or a dev server)
# to call this API from the browser. Wide open here since this is a local portfolio project —
# a real deployment would restrict allow_origins to the actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(match.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Resume Screening Assistant API is running"}
