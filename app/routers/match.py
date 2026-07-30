from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Resume, Job, Match, User
from app.schemas import MatchRequest, MatchOut
from app.auth import get_current_user
from app.ai import get_similarity_score, compare_skills

router = APIRouter(prefix="/match", tags=["match"])


@router.post("", response_model=MatchOut, status_code=201)
def create_match(
    match_in: MatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == match_in.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job = db.query(Job).filter(Job.id == match_in.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    score = get_similarity_score(resume.raw_text, job.description)
    matched_skills, missing_skills = compare_skills(resume.raw_text, job.required_skills)

    match = Match(
        resume_id=resume.id,
        job_id=job.id,
        score=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@router.get("/{match_id}", response_model=MatchOut)
def get_match(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match