from datetime import datetime
 
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
 
from app.database import Base
 
 
class User(Base):
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
 
    resumes = relationship("Resume", back_populates="owner")
    jobs = relationship("Job", back_populates="owner")
 
 
class Resume(Base):
    __tablename__ = "resumes"
 
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
 
    owner = relationship("User", back_populates="resumes")
 
 
class Job(Base):
    __tablename__ = "jobs"
 
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)  # e.g. ["Python", "Docker"]
    created_at = Column(DateTime, default=datetime.utcnow)
 
    owner = relationship("User", back_populates="jobs")
 
 
class Match(Base):
    __tablename__ = "matches"
 
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    score = Column(Float, nullable=False)
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)