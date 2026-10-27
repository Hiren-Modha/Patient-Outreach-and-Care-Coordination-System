# Agentic AI Patient Outreach & Care Coordination System
### Built with IBM Bob · IBM Granite · Python · FastAPI · SQLite

---

## What This Project Does

This is a **fully functional web application** that simulates an AI-assisted care
coordination system for patients with chronic conditions (e.g. Type 2 Diabetes).

It demonstrates how AI agents can:
- Review AI-generated patient risk rankings
- Identify care barriers (transport, language, financial, social isolation)
- Flag missing clinical information
- Generate person-centred outreach plans
- Escalate urgent cases for senior clinician review
- Track all actions through a human-in-the-loop approval workflow

> **Responsible AI Notice:** All data is synthetic. The system does not diagnose
> patients or replace clinical judgement. Every AI recommendation requires
> review and approval by a qualified healthcare professional.

---

## Quick Start (5 steps)

### Step 1 — Make sure Python is installed

```bash
python --version   # needs Python 3.9 or newer
```

### Step 2 — Open the project folder

```bash
cd patient_outreach_system
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Start the server

```bash
python -m uvicorn main:app --reload
```

The server will:
- Create the SQLite database automatically
- Seed 10 synthetic patients with care barriers, outreach plans, escalations, and reviews

### Step 5 — Open your browser

Go to: **http://localhost:8000**

---

## Pages & Features

| Page | URL | What it does |
|------|-----|--------------|
| **Dashboard** | `/` | Overview tiles, outreach status bars, risk donut chart |
| **Patient Register** | `/patients` | Full list with search/filter; risk badges; HbA1c colours |
| **Patient Detail** | `/patients/{id}` | Full profile, AI explanation, care barriers, outreach plan, review modal |
| **Outreach Plans** | `/outreach` | All plans; update status with one click |
| **Escalations** | `/escalations` | Open and resolved escalations; resolve with notes |
| **Human Reviews** | `/reviews` | Audit trail of all clinician approvals |
| **Reports** | `/reports` | Charts, barrier analysis, responsible AI disclosure |
| **API Docs** | `/docs` | Auto-generated FastAPI interactive API docs |

---

## AI Agents Explained (Simply)

| Agent | What it does |
|-------|-------------|
| **Risk Ranking Review** | Checks if the AI's risk score is consistent with clinical data |
| **Care Barrier Identification** | Reads documented barriers and recommends mitigations |
| **Outreach Planning** | Picks the best contact method, role, and timeline |
| **Escalation** | Flags urgent cases that need immediate senior clinician attention |
| **IBM Granite Explanation** | Generates a plain-English summary of why a patient needs outreach |

---

## Optional: IBM Granite API (Real AI)

By default the system uses a built-in **rule-based AI engine** — no API key needed.

To use real IBM Granite:

1. Get an IBM Cloud API key from https://cloud.ibm.com
2. Set environment variables before starting the server:

```bash
# Windows
set GRANITE_API_KEY=your_ibm_cloud_api_key
set GRANITE_API_URL=https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29

# macOS/Linux
export GRANITE_API_KEY=your_ibm_cloud_api_key
export GRANITE_API_URL=https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29

python -m uvicorn main:app --reload
```

---

## Running the Tests

```bash
python test_app.py
```

Expected output: `RESULTS: 22/22 passed  ALL PASSED`

---

## Project Structure

```
patient_outreach_system/
  main.py              ← FastAPI app, all routes and API endpoints
  database.py          ← SQLAlchemy models (Patient, CareBarrier, OutreachPlan, …)
  seed_data.py         ← 10 synthetic patients with full clinical profiles
  test_app.py          ← Automated test suite (22 tests)
  requirements.txt     ← Python dependencies
  agents/
    granite_agent.py   ← All AI agents + IBM Granite integration
  templates/
    base.html          ← Shared layout with sidebar navigation
    dashboard.html     ← Main dashboard with charts
    patients.html      ← Patient register with search/filter
    patient_detail.html← Full patient profile + AI tools
    outreach.html      ← Outreach plan management
    escalations.html   ← Escalation log
    reviews.html       ← Human review audit trail
    reports.html       ← Analytics and responsible AI disclosure
  static/
    css/style.css      ← All CSS styles
    js/app.js          ← Shared JavaScript utilities
```

---

## Responsible AI Guardrails

- All data is **synthetic** — no real patients
- AI **never diagnoses** or recommends treatments
- All outreach plans require **human clinical approval** before action
- Missing data and uncertainty are **explicitly flagged**
- **Human-in-the-loop** review is built into every workflow
- Escalation routes ensure **senior clinician oversight** for urgent cases

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| AI Engine | IBM Granite (API) / Rule-based fallback |
| Development | IBM Bob |
| Backend | Python 3.9+, FastAPI |
| Database | SQLite via SQLAlchemy |
| Templates | Jinja2 |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Testing | Python standard library (urllib, threading) |
