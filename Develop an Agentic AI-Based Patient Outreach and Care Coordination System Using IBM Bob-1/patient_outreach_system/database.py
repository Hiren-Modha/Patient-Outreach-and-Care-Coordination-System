"""
database.py – SQLAlchemy models and database setup for the
Patient Outreach & Care Coordination System.
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    Text, DateTime, Boolean, ForeignKey, Enum
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import enum

DATABASE_URL = "sqlite:///./patient_outreach.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── Enums ───────────────────────────────────────────────────────────────────

class RiskLevel(str, enum.Enum):
    LOW    = "Low"
    MEDIUM = "Medium"
    HIGH   = "High"
    URGENT = "Urgent"

class OutreachStatus(str, enum.Enum):
    PENDING    = "Pending"
    CONTACTED  = "Contacted"
    NO_ANSWER  = "No Answer"
    SCHEDULED  = "Scheduled"
    COMPLETED  = "Completed"
    ESCALATED  = "Escalated"

class ReviewStatus(str, enum.Enum):
    PENDING  = "Pending Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    FLAGGED  = "Flagged for Escalation"


# ─── Models ──────────────────────────────────────────────────────────────────

class Patient(Base):
    __tablename__ = "patients"

    id                 = Column(Integer, primary_key=True, index=True)
    name               = Column(String(100), nullable=False)
    age                = Column(Integer)
    gender             = Column(String(20))
    condition          = Column(String(100))          # primary chronic condition
    hba1c              = Column(Float)                # diabetes marker
    blood_pressure     = Column(String(20))
    last_visit         = Column(String(20))           # date string YYYY-MM-DD
    phone              = Column(String(30))
    email              = Column(String(100))
    address            = Column(String(200))
    insurance          = Column(String(50))
    language           = Column(String(50), default="English")
    ai_risk_score      = Column(Float)                # 0–100
    ai_risk_level      = Column(String(20))
    reviewed_risk_level= Column(String(20))           # after human review
    missing_data_flags = Column(Text)                 # JSON list
    created_at         = Column(DateTime, default=datetime.utcnow)

    outreach_plans  = relationship("OutreachPlan",  back_populates="patient", cascade="all, delete")
    care_barriers   = relationship("CareBarrier",   back_populates="patient", cascade="all, delete")
    escalations     = relationship("Escalation",    back_populates="patient", cascade="all, delete")
    review_records  = relationship("ReviewRecord",  back_populates="patient", cascade="all, delete")


class CareBarrier(Base):
    __tablename__ = "care_barriers"

    id           = Column(Integer, primary_key=True, index=True)
    patient_id   = Column(Integer, ForeignKey("patients.id"))
    barrier_type = Column(String(100))  # Transportation, Language, Financial, etc.
    description  = Column(Text)
    severity     = Column(String(20))   # Low / Medium / High
    created_at   = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="care_barriers")


class OutreachPlan(Base):
    __tablename__ = "outreach_plans"

    id              = Column(Integer, primary_key=True, index=True)
    patient_id      = Column(Integer, ForeignKey("patients.id"))
    contact_method  = Column(String(50))  # Phone, SMS, Email, Home Visit
    next_step       = Column(Text)
    responsible_role= Column(String(100))
    follow_up_date  = Column(String(20))
    status          = Column(String(30), default="Pending")
    ai_rationale    = Column(Text)        # Granite-generated explanation
    notes           = Column(Text)
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("Patient", back_populates="outreach_plans")


class Escalation(Base):
    __tablename__ = "escalations"

    id           = Column(Integer, primary_key=True, index=True)
    patient_id   = Column(Integer, ForeignKey("patients.id"))
    reason       = Column(Text)
    urgency      = Column(String(20))  # Routine / Urgent / Emergency
    assigned_to  = Column(String(100))
    resolved     = Column(Boolean, default=False)
    resolution   = Column(Text)
    created_at   = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="escalations")


class ReviewRecord(Base):
    __tablename__ = "review_records"

    id            = Column(Integer, primary_key=True, index=True)
    patient_id    = Column(Integer, ForeignKey("patients.id"))
    reviewer_name = Column(String(100))
    review_status = Column(String(50), default="Pending Review")
    comments      = Column(Text)
    approved_plan = Column(Text)
    created_at    = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="review_records")


# ─── Dependency helper ────────────────────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
