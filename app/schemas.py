from datetime import datetime
from pydantic import BaseModel, EmailStr


# ---------- Auth / User ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Resume ----------

class ResumeOut(BaseModel):
    id: int
    filename: str
    raw_text: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Job ----------

class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: list[str] = []


class JobOut(BaseModel):
    id: int
    title: str
    description: str
    required_skills: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Match ----------

class MatchRequest(BaseModel):
    resume_id: int
    job_id: int


class MatchOut(BaseModel):
    id: int
    resume_id: int
    job_id: int
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Dashboard ----------

class DashboardOut(BaseModel):
    resumes_uploaded: int
    jobs_created: int
    average_match_score: float