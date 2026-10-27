"""
main.py – FastAPI application for the
Agentic AI Patient Outreach & Care Coordination System.

Start the server:
    uvicorn main:app --reload
"""

import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import (
    get_db, init_db,
    Patient, CareBarrier, OutreachPlan, Escalation, ReviewRecord,
)
from seed_data import seed
from agents.granite_agent import (
    get_granite_explanation,
    review_ai_risk_ranking,
    identify_care_barriers,
    generate_outreach_plan,
    should_escalate,
)

# ─── App setup ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed()
    yield


app = FastAPI(
    title="Patient Outreach & Care Coordination System",
    description="Agentic AI system powered by IBM Bob & IBM Granite",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ─── Pydantic schemas ─────────────────────────────────────────────────────────

class OutreachUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class ReviewCreate(BaseModel):
    reviewer_name: str
    review_status: str
    comments: Optional[str] = None
    approved_plan: Optional[str] = None

class EscalationCreate(BaseModel):
    reason: str
    urgency: str
    assigned_to: str

class PatientUpdate(BaseModel):
    reviewed_risk_level: Optional[str] = None
    notes: Optional[str] = None


# ─── Helper ───────────────────────────────────────────────────────────────────

def patient_to_dict(p: Patient) -> dict:
    try:
        missing = json.loads(p.missing_data_flags) if p.missing_data_flags else []
    except Exception:
        missing = []
    return {
        "id": p.id,
        "name": p.name,
        "age": p.age,
        "gender": p.gender,
        "condition": p.condition,
        "hba1c": p.hba1c,
        "blood_pressure": p.blood_pressure,
        "last_visit": p.last_visit,
        "phone": p.phone,
        "email": p.email,
        "address": p.address,
        "insurance": p.insurance,
        "language": p.language,
        "ai_risk_score": p.ai_risk_score,
        "ai_risk_level": p.ai_risk_level,
        "reviewed_risk_level": p.reviewed_risk_level,
        "missing_data_flags": missing,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE ROUTES (HTML)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    patients = db.query(Patient).all()

    total       = len(patients)
    urgent      = sum(1 for p in patients if p.reviewed_risk_level == "Urgent")
    high        = sum(1 for p in patients if p.reviewed_risk_level == "High")
    medium      = sum(1 for p in patients if p.reviewed_risk_level == "Medium")
    low         = sum(1 for p in patients if p.reviewed_risk_level == "Low")
    escalations = db.query(Escalation).filter(Escalation.resolved == False).count()
    pending_reviews = db.query(ReviewRecord).filter(ReviewRecord.review_status == "Pending Review").count()

    outreach    = db.query(OutreachPlan).all()
    completed   = sum(1 for o in outreach if o.status == "Completed")
    pending     = sum(1 for o in outreach if o.status == "Pending")
    contacted   = sum(1 for o in outreach if o.status == "Contacted")
    no_answer   = sum(1 for o in outreach if o.status == "No Answer")
    scheduled   = sum(1 for o in outreach if o.status == "Scheduled")
    escalated   = sum(1 for o in outreach if o.status == "Escalated")

    recent_outreach = (
        db.query(OutreachPlan)
        .order_by(OutreachPlan.created_at.desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse(request, "dashboard.html", {
        "total": total, "urgent": urgent, "high": high, "medium": medium, "low": low,
        "open_escalations": escalations,
        "pending_reviews": pending_reviews,
        "outreach_stats": {
            "completed": completed, "pending": pending, "contacted": contacted,
            "no_answer": no_answer, "scheduled": scheduled, "escalated": escalated,
        },
        "recent_outreach": recent_outreach,
    })


@app.get("/patients", response_class=HTMLResponse)
async def patients_page(request: Request, db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return templates.TemplateResponse(request, "patients.html", {
        "patients": patients,
    })


@app.get("/patients/{patient_id}", response_class=HTMLResponse)
async def patient_detail(request: Request, patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    barriers    = db.query(CareBarrier).filter(CareBarrier.patient_id == patient_id).all()
    outreach    = db.query(OutreachPlan).filter(OutreachPlan.patient_id == patient_id).all()
    escalations = db.query(Escalation).filter(Escalation.patient_id == patient_id).all()
    reviews     = db.query(ReviewRecord).filter(ReviewRecord.patient_id == patient_id).all()

    # Agent analyses
    p_dict       = patient_to_dict(patient)
    risk_review  = review_ai_risk_ranking(p_dict)
    barrier_info = identify_care_barriers([{"barrier_type": b.barrier_type, "severity": b.severity} for b in barriers])
    escalation   = should_escalate(p_dict, [{"barrier_type": b.barrier_type} for b in barriers])

    try:
        missing = json.loads(patient.missing_data_flags) if patient.missing_data_flags else []
    except Exception:
        missing = []

    return templates.TemplateResponse(request, "patient_detail.html", {
        "patient": patient,
        "missing_flags": missing,
        "barriers": barriers,
        "outreach": outreach,
        "escalations": escalations,
        "reviews": reviews,
        "risk_review": risk_review,
        "barrier_info": barrier_info,
        "escalation_check": escalation,
    })


@app.get("/outreach", response_class=HTMLResponse)
async def outreach_page(request: Request, db: Session = Depends(get_db)):
    plans = (
        db.query(OutreachPlan)
        .order_by(OutreachPlan.follow_up_date.asc())
        .all()
    )
    return templates.TemplateResponse(request, "outreach.html", {
        "plans": plans,
    })


@app.get("/escalations", response_class=HTMLResponse)
async def escalations_page(request: Request, db: Session = Depends(get_db)):
    open_esc   = db.query(Escalation).filter(Escalation.resolved == False).all()
    closed_esc = db.query(Escalation).filter(Escalation.resolved == True).all()
    return templates.TemplateResponse(request, "escalations.html", {
        "open_escalations": open_esc,
        "closed_escalations": closed_esc,
    })


@app.get("/reviews", response_class=HTMLResponse)
async def reviews_page(request: Request, db: Session = Depends(get_db)):
    reviews = db.query(ReviewRecord).order_by(ReviewRecord.created_at.desc()).all()
    return templates.TemplateResponse(request, "reviews.html", {
        "reviews": reviews,
    })


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request, db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    plans    = db.query(OutreachPlan).all()
    barriers = db.query(CareBarrier).all()

    # Barrier type counts
    barrier_counts = {}
    for b in barriers:
        barrier_counts[b.barrier_type] = barrier_counts.get(b.barrier_type, 0) + 1

    # Outreach status counts
    status_counts = {}
    for p in plans:
        status_counts[p.status] = status_counts.get(p.status, 0) + 1

    # Risk distribution
    risk_dist = {"Urgent": 0, "High": 0, "Medium": 0, "Low": 0}
    for p in patients:
        level = p.reviewed_risk_level or "Low"
        risk_dist[level] = risk_dist.get(level, 0) + 1

    return templates.TemplateResponse(request, "reports.html", {
        "patients": patients,
        "barrier_counts": barrier_counts,
        "status_counts": status_counts,
        "risk_dist": risk_dist,
        "total_patients": len(patients),
        "total_plans": len(plans),
        "total_barriers": len(barriers),
    })


# ═══════════════════════════════════════════════════════════════════════════════
# API ROUTES (JSON)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/patients")
def api_get_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return [patient_to_dict(p) for p in patients]


@app.get("/api/patients/{patient_id}")
def api_get_patient(patient_id: int, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient_to_dict(p)


@app.patch("/api/patients/{patient_id}")
def api_update_patient(patient_id: int, update: PatientUpdate, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    if update.reviewed_risk_level:
        p.reviewed_risk_level = update.reviewed_risk_level
    db.commit()
    return {"message": "Updated", "patient": patient_to_dict(p)}


@app.get("/api/patients/{patient_id}/explain")
def api_explain_patient(patient_id: int, db: Session = Depends(get_db)):
    """IBM Granite / AI Rule Engine explanation for a patient."""
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    explanation = get_granite_explanation(patient_to_dict(p))
    return {"patient_id": patient_id, "patient_name": p.name, "explanation": explanation}


@app.get("/api/patients/{patient_id}/generate-plan")
def api_generate_plan(patient_id: int, db: Session = Depends(get_db)):
    """Outreach Planning Agent: auto-generate an outreach plan."""
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    barriers = db.query(CareBarrier).filter(CareBarrier.patient_id == patient_id).all()
    b_list   = [{"barrier_type": b.barrier_type, "severity": b.severity} for b in barriers]
    plan     = generate_outreach_plan(patient_to_dict(p), b_list)
    return plan


@app.post("/api/outreach/{plan_id}/status")
def api_update_outreach_status(plan_id: int, update: OutreachUpdate, db: Session = Depends(get_db)):
    plan = db.query(OutreachPlan).filter(OutreachPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Outreach plan not found")
    plan.status = update.status
    if update.notes:
        plan.notes = update.notes
    plan.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Status updated", "plan_id": plan_id, "status": plan.status}


@app.post("/api/patients/{patient_id}/review")
def api_create_review(patient_id: int, review: ReviewCreate, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    rec = ReviewRecord(
        patient_id    = patient_id,
        reviewer_name = review.reviewer_name,
        review_status = review.review_status,
        comments      = review.comments,
        approved_plan = review.approved_plan,
    )
    db.add(rec)
    db.commit()
    return {"message": "Review saved", "review_id": rec.id}


@app.post("/api/patients/{patient_id}/escalate")
def api_escalate(patient_id: int, esc: EscalationCreate, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    obj = Escalation(
        patient_id  = patient_id,
        reason      = esc.reason,
        urgency     = esc.urgency,
        assigned_to = esc.assigned_to,
    )
    db.add(obj)
    # Also update outreach plan to Escalated
    for plan in db.query(OutreachPlan).filter(OutreachPlan.patient_id == patient_id).all():
        plan.status = "Escalated"
    db.commit()
    return {"message": "Escalated", "escalation_id": obj.id}


@app.patch("/api/escalations/{esc_id}/resolve")
def api_resolve_escalation(esc_id: int, resolution: str = "", db: Session = Depends(get_db)):
    esc = db.query(Escalation).filter(Escalation.id == esc_id).first()
    if not esc:
        raise HTTPException(status_code=404, detail="Escalation not found")
    esc.resolved   = True
    esc.resolution = resolution
    db.commit()
    return {"message": "Escalation resolved"}


@app.get("/api/dashboard/stats")
def api_dashboard_stats(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    outreach = db.query(OutreachPlan).all()
    return {
        "total_patients": len(patients),
        "risk_distribution": {
            "Urgent": sum(1 for p in patients if p.reviewed_risk_level == "Urgent"),
            "High":   sum(1 for p in patients if p.reviewed_risk_level == "High"),
            "Medium": sum(1 for p in patients if p.reviewed_risk_level == "Medium"),
            "Low":    sum(1 for p in patients if p.reviewed_risk_level == "Low"),
        },
        "outreach_status": {
            s: sum(1 for o in outreach if o.status == s)
            for s in ["Pending", "Contacted", "No Answer", "Scheduled", "Completed", "Escalated"]
        },
        "open_escalations": db.query(Escalation).filter(Escalation.resolved == False).count(),
        "pending_reviews":  db.query(ReviewRecord).filter(ReviewRecord.review_status == "Pending Review").count(),
    }
