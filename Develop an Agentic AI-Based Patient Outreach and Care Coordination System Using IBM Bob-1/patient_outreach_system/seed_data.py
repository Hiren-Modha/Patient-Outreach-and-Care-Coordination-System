"""
seed_data.py – Synthetic patient dataset for the
Patient Outreach & Care Coordination System.

Run once:  python seed_data.py
"""

import json
from database import SessionLocal, init_db, Patient, CareBarrier, OutreachPlan, Escalation, ReviewRecord

# ─── Synthetic patients ───────────────────────────────────────────────────────

PATIENTS = [
    {
        "name": "Margaret Thompson", "age": 67, "gender": "Female",
        "condition": "Type 2 Diabetes", "hba1c": 9.2, "blood_pressure": "148/92",
        "last_visit": "2024-08-15", "phone": "555-0101", "email": "m.thompson@email.com",
        "address": "42 Oak Street, Springfield", "insurance": "Medicare",
        "language": "English", "ai_risk_score": 87.4, "ai_risk_level": "High",
        "reviewed_risk_level": "Urgent",
        "missing_data_flags": json.dumps(["Foot examination record missing", "Retinal screening overdue"]),
    },
    {
        "name": "Carlos Rivera", "age": 54, "gender": "Male",
        "condition": "Type 2 Diabetes", "hba1c": 8.1, "blood_pressure": "135/85",
        "last_visit": "2024-10-02", "phone": "555-0102", "email": "c.rivera@email.com",
        "address": "18 Maple Ave, Riverside", "insurance": "Medicaid",
        "language": "Spanish", "ai_risk_score": 72.1, "ai_risk_level": "High",
        "reviewed_risk_level": "High",
        "missing_data_flags": json.dumps(["No interpreter documented", "Transport barrier unresolved"]),
    },
    {
        "name": "Linda Chen", "age": 61, "gender": "Female",
        "condition": "Type 2 Diabetes + Hypertension", "hba1c": 7.6, "blood_pressure": "152/96",
        "last_visit": "2024-09-20", "phone": "555-0103", "email": "l.chen@email.com",
        "address": "7 Pine Road, Lakewood", "insurance": "BlueCross",
        "language": "Mandarin", "ai_risk_score": 65.8, "ai_risk_level": "Medium",
        "reviewed_risk_level": "High",
        "missing_data_flags": json.dumps(["Blood pressure log incomplete"]),
    },
    {
        "name": "James O'Brien", "age": 71, "gender": "Male",
        "condition": "Type 2 Diabetes", "hba1c": 10.4, "blood_pressure": "160/100",
        "last_visit": "2024-06-05", "phone": "555-0104", "email": "j.obrien@email.com",
        "address": "91 Elm Drive, Greenfield", "insurance": "Medicare",
        "language": "English", "ai_risk_score": 93.5, "ai_risk_level": "Urgent",
        "reviewed_risk_level": "Urgent",
        "missing_data_flags": json.dumps(["Nephrology referral not completed", "No emergency contact on file"]),
    },
    {
        "name": "Aisha Patel", "age": 45, "gender": "Female",
        "condition": "Pre-Diabetes", "hba1c": 6.3, "blood_pressure": "122/78",
        "last_visit": "2024-11-10", "phone": "555-0105", "email": "a.patel@email.com",
        "address": "55 Birch Lane, Millbrook", "insurance": "Aetna",
        "language": "English", "ai_risk_score": 42.0, "ai_risk_level": "Medium",
        "reviewed_risk_level": "Medium",
        "missing_data_flags": json.dumps([]),
    },
    {
        "name": "Robert Johnson", "age": 58, "gender": "Male",
        "condition": "Type 2 Diabetes + CHD", "hba1c": 8.8, "blood_pressure": "145/90",
        "last_visit": "2024-07-18", "phone": "555-0106", "email": "r.johnson@email.com",
        "address": "33 Cedar Court, Westport", "insurance": "UnitedHealth",
        "language": "English", "ai_risk_score": 81.2, "ai_risk_level": "High",
        "reviewed_risk_level": "High",
        "missing_data_flags": json.dumps(["Cardiology follow-up pending", "Medication reconciliation needed"]),
    },
    {
        "name": "Fatima Al-Hassan", "age": 49, "gender": "Female",
        "condition": "Type 2 Diabetes", "hba1c": 7.9, "blood_pressure": "130/82",
        "last_visit": "2024-10-25", "phone": "555-0107", "email": "f.alhassan@email.com",
        "address": "12 Willow Way, Northside", "insurance": "Cigna",
        "language": "Arabic", "ai_risk_score": 58.7, "ai_risk_level": "Medium",
        "reviewed_risk_level": "Medium",
        "missing_data_flags": json.dumps(["Language-concordant provider not assigned"]),
    },
    {
        "name": "David Kim", "age": 63, "gender": "Male",
        "condition": "Type 2 Diabetes + CKD", "hba1c": 9.5, "blood_pressure": "155/95",
        "last_visit": "2024-05-30", "phone": "555-0108", "email": "d.kim@email.com",
        "address": "88 Spruce Street, Eastside", "insurance": "Medicare",
        "language": "Korean", "ai_risk_score": 89.0, "ai_risk_level": "Urgent",
        "reviewed_risk_level": "Urgent",
        "missing_data_flags": json.dumps(["Renal diet counselling not initiated", "Home visit recommended"]),
    },
    {
        "name": "Susan Wallace", "age": 52, "gender": "Female",
        "condition": "Type 2 Diabetes", "hba1c": 6.9, "blood_pressure": "125/80",
        "last_visit": "2024-11-05", "phone": "555-0109", "email": "s.wallace@email.com",
        "address": "20 Ash Avenue, Southtown", "insurance": "BlueCross",
        "language": "English", "ai_risk_score": 35.5, "ai_risk_level": "Low",
        "reviewed_risk_level": "Low",
        "missing_data_flags": json.dumps([]),
    },
    {
        "name": "Michael Okafor", "age": 41, "gender": "Male",
        "condition": "Pre-Diabetes + Obesity", "hba1c": 6.1, "blood_pressure": "128/84",
        "last_visit": "2024-09-14", "phone": "555-0110", "email": "m.okafor@email.com",
        "address": "75 Poplar Place, Midtown", "insurance": "Medicaid",
        "language": "English", "ai_risk_score": 48.3, "ai_risk_level": "Medium",
        "reviewed_risk_level": "Medium",
        "missing_data_flags": json.dumps(["Lifestyle intervention referral missing"]),
    },
]

CARE_BARRIERS = [
    {"patient_idx": 0, "barrier_type": "Transportation", "description": "Patient lives 25 miles from nearest clinic; no personal vehicle.", "severity": "High"},
    {"patient_idx": 0, "barrier_type": "Financial",      "description": "Fixed income; reports difficulty affording medications.", "severity": "High"},
    {"patient_idx": 1, "barrier_type": "Language",       "description": "Primary language is Spanish; limited English proficiency.", "severity": "High"},
    {"patient_idx": 1, "barrier_type": "Transportation", "description": "Relies on public transport; appointment times are restrictive.", "severity": "Medium"},
    {"patient_idx": 2, "barrier_type": "Language",       "description": "Prefers Mandarin; daughter assists but not always available.", "severity": "Medium"},
    {"patient_idx": 3, "barrier_type": "Social Isolation","description": "Lives alone; no listed emergency contact.", "severity": "High"},
    {"patient_idx": 3, "barrier_type": "Transportation", "description": "Cannot drive due to vision impairment.", "severity": "High"},
    {"patient_idx": 5, "barrier_type": "Financial",      "description": "Reports concern about co-pay costs for specialist visits.", "severity": "Medium"},
    {"patient_idx": 6, "barrier_type": "Language",       "description": "Communicates primarily in Arabic; needs interpreter.", "severity": "High"},
    {"patient_idx": 6, "barrier_type": "Cultural",       "description": "Cultural preference for female clinician not always accommodated.", "severity": "Medium"},
    {"patient_idx": 7, "barrier_type": "Transportation", "description": "Uses wheelchair; needs accessible transport.", "severity": "High"},
    {"patient_idx": 7, "barrier_type": "Health Literacy","description": "Difficulty understanding written care instructions.", "severity": "Medium"},
    {"patient_idx": 9, "barrier_type": "Financial",      "description": "Uninsured gaps; concern about prescription costs.", "severity": "Medium"},
]

OUTREACH_PLANS = [
    {"patient_idx": 0, "contact_method": "Phone", "next_step": "Schedule urgent diabetes review with primary care; arrange medical transport.", "responsible_role": "Care Coordinator", "follow_up_date": "2025-01-10", "status": "Pending", "ai_rationale": "HbA1c of 9.2% with missed foot and retinal checks indicates high complication risk. Urgent review recommended within 2 weeks."},
    {"patient_idx": 1, "contact_method": "SMS",   "next_step": "Arrange Spanish-speaking navigator; book interpreter for next appointment.", "responsible_role": "Community Health Worker", "follow_up_date": "2025-01-12", "status": "Contacted", "ai_rationale": "Language and transport barriers compound clinical risk. Spanish-language outreach and interpreter booking should precede clinical scheduling."},
    {"patient_idx": 2, "contact_method": "Phone", "next_step": "Review blood pressure management; liaise with bilingual nurse practitioner.", "responsible_role": "Nurse Practitioner", "follow_up_date": "2025-01-15", "status": "Scheduled", "ai_rationale": "Hypertension with inadequate BP log represents a monitoring gap. Coordinated bilingual follow-up will support adherence."},
    {"patient_idx": 3, "contact_method": "Home Visit", "next_step": "Immediate home visit to assess living situation; expedite nephrology referral.", "responsible_role": "Social Worker + GP", "follow_up_date": "2025-01-08", "status": "Escalated", "ai_rationale": "HbA1c 10.4%, BP 160/100, CKD risk, lives alone, no emergency contact. Multi-professional response required."},
    {"patient_idx": 4, "contact_method": "Email", "next_step": "Send diabetes prevention programme information; schedule annual review.", "responsible_role": "Practice Nurse", "follow_up_date": "2025-02-01", "status": "Pending", "ai_rationale": "Pre-diabetic with stable markers. Low-intensity lifestyle-focused outreach is appropriate."},
    {"patient_idx": 5, "contact_method": "Phone", "next_step": "Confirm cardiology follow-up; review medication list with pharmacist.", "responsible_role": "Care Coordinator", "follow_up_date": "2025-01-20", "status": "No Answer", "ai_rationale": "Cardiology pending and medication reconciliation gap present elevated cardiovascular risk. Pharmacist review recommended."},
    {"patient_idx": 6, "contact_method": "Phone", "next_step": "Assign Arabic-speaking navigator; review cultural care preferences.", "responsible_role": "Community Health Worker", "follow_up_date": "2025-01-18", "status": "Pending", "ai_rationale": "Language barrier and cultural needs require navigator involvement before clinical engagement."},
    {"patient_idx": 7, "contact_method": "Home Visit", "next_step": "Arrange accessible transport; initiate renal diet counselling; health literacy support.", "responsible_role": "District Nurse + Dietitian", "follow_up_date": "2025-01-09", "status": "Escalated", "ai_rationale": "CKD with uncontrolled diabetes requires renal diet urgently. Accessibility barrier and low health literacy require in-person support."},
    {"patient_idx": 8, "contact_method": "Email", "next_step": "Routine annual review reminder; no urgent action required.", "responsible_role": "Practice Nurse", "follow_up_date": "2025-03-01", "status": "Completed", "ai_rationale": "Stable markers, well-managed condition, recent visit. Routine monitoring is sufficient."},
    {"patient_idx": 9, "contact_method": "SMS",   "next_step": "Refer to lifestyle intervention programme; explore medication assistance schemes.", "responsible_role": "Care Coordinator", "follow_up_date": "2025-01-25", "status": "Pending", "ai_rationale": "Pre-diabetes with obesity and financial concern warrants lifestyle intervention referral and medication cost support review."},
]

ESCALATIONS = [
    {"patient_idx": 3, "reason": "HbA1c 10.4%, BP 160/100, lives alone, no emergency contact, nephrology referral not completed. Immediate multi-professional review required.", "urgency": "Urgent", "assigned_to": "Dr. Sarah Malik (Lead GP)", "resolved": False},
    {"patient_idx": 7, "reason": "CKD with uncontrolled diabetes (HbA1c 9.5%), no renal diet initiated, wheelchair user with no accessible transport arranged.", "urgency": "Urgent", "assigned_to": "Dr. Raj Patel (Endocrinology)", "resolved": False},
    {"patient_idx": 0, "reason": "Overdue foot and retinal examinations represent significant complication risk in patient with known high HbA1c.", "urgency": "Routine", "assigned_to": "Practice Nurse Lead", "resolved": True, "resolution": "Retinal screening booked for 2025-01-14. Foot examination scheduled same date."},
]

REVIEWS = [
    {"patient_idx": 0, "reviewer_name": "Dr. Sarah Malik", "review_status": "Approved", "comments": "Agreed – urgent transport and clinical review needed within 2 weeks.", "approved_plan": "Arrange medical transport; schedule combined podiatry/retinal/diabetes review 2025-01-14."},
    {"patient_idx": 3, "reviewer_name": "Dr. Sarah Malik", "review_status": "Flagged for Escalation", "comments": "Patient requires immediate home assessment. Social services to be notified.", "approved_plan": "Home visit by social worker and district nurse by 2025-01-08. Emergency contact to be established."},
    {"patient_idx": 7, "reviewer_name": "Dr. Raj Patel",   "review_status": "Flagged for Escalation", "comments": "Renal diet and accessible transport are urgent. Case escalated to renal team.", "approved_plan": "Dietitian referral and accessible transport arranged. Renal team notified."},
    {"patient_idx": 4, "reviewer_name": "Nurse Practitioner Jones", "review_status": "Approved", "comments": "Low risk – email outreach and annual review is appropriate.", "approved_plan": "Email diabetes prevention programme info; annual review February 2025."},
]


def seed():
    init_db()
    db = SessionLocal()

    # Skip if already seeded
    if db.query(Patient).count() > 0:
        print("Database already seeded – skipping.")
        db.close()
        return

    patient_objs = []
    for p in PATIENTS:
        obj = Patient(**p)
        db.add(obj)
        patient_objs.append(obj)
    db.flush()  # get IDs

    for b in CARE_BARRIERS:
        obj = CareBarrier(
            patient_id=patient_objs[b["patient_idx"]].id,
            barrier_type=b["barrier_type"],
            description=b["description"],
            severity=b["severity"],
        )
        db.add(obj)

    for o in OUTREACH_PLANS:
        obj = OutreachPlan(
            patient_id=patient_objs[o["patient_idx"]].id,
            contact_method=o["contact_method"],
            next_step=o["next_step"],
            responsible_role=o["responsible_role"],
            follow_up_date=o["follow_up_date"],
            status=o["status"],
            ai_rationale=o["ai_rationale"],
        )
        db.add(obj)

    for e in ESCALATIONS:
        obj = Escalation(
            patient_id=patient_objs[e["patient_idx"]].id,
            reason=e["reason"],
            urgency=e["urgency"],
            assigned_to=e["assigned_to"],
            resolved=e.get("resolved", False),
            resolution=e.get("resolution"),
        )
        db.add(obj)

    for r in REVIEWS:
        obj = ReviewRecord(
            patient_id=patient_objs[r["patient_idx"]].id,
            reviewer_name=r["reviewer_name"],
            review_status=r["review_status"],
            comments=r["comments"],
            approved_plan=r["approved_plan"],
        )
        db.add(obj)

    db.commit()
    db.close()
    print(f"Seeded {len(PATIENTS)} patients with barriers, outreach plans, escalations, and reviews.")


if __name__ == "__main__":
    seed()
