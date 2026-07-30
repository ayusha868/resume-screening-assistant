from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Resume, Job, Match, User
from app.schemas import DashboardOut
from app.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resumes_uploaded = db.query(Resume).filter(Resume.owner_id == current_user.id).count()
    jobs_created = db.query(Job).filter(Job.owner_id == current_user.id).count()

    # Average score across matches involving this user's own resumes.
    avg_score = (
        db.query(func.avg(Match.score))
        .join(Resume, Match.resume_id == Resume.id)
        .filter(Resume.owner_id == current_user.id)
        .scalar()
    )

    return DashboardOut(
        resumes_uploaded=resumes_uploaded,
        jobs_created=jobs_created,
        average_match_score=round(avg_score, 2) if avg_score else 0.0,
    )