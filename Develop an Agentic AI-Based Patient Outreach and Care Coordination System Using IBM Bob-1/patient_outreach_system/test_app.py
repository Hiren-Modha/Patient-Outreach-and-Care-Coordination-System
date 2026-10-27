"""
test_app.py - Automated tests for Patient Outreach System
Run: python test_app.py
"""
import sys
import threading
import time
import urllib.request
import urllib.error
import http.client
import json

sys.path.insert(0, ".")
import uvicorn

PASSED = 0
FAILED = 0
BASE = "http://127.0.0.1:8789"


def run_server():
    uvicorn.run("main:app", host="127.0.0.1", port=8789, log_level="error")


def test_route(path, method="GET", post_data=None, expected_status=200):
    global PASSED, FAILED
    url = BASE + path
    try:
        req = urllib.request.Request(url)
        if post_data is not None:
            req.add_header("Content-Type", "application/json")
            req.data = json.dumps(post_data).encode()
            req.method = method
        with urllib.request.urlopen(req, timeout=5) as r:
            status = r.status
            r.read()
        if status == expected_status:
            PASSED += 1
            print(f"  PASS  {method:6s} {path} -> {status}")
        else:
            FAILED += 1
            print(f"  FAIL  {method:6s} {path} -> {status} (expected {expected_status})")
    except urllib.error.HTTPError as e:
        if e.code == expected_status:
            PASSED += 1
            print(f"  PASS  {method:6s} {path} -> {e.code}")
        else:
            FAILED += 1
            print(f"  FAIL  {method:6s} {path} -> {e.code} (expected {expected_status})")
    except Exception as e:
        FAILED += 1
        print(f"  FAIL  {method:6s} {path} -> ERROR: {e}")


def main():
    global PASSED, FAILED
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(3)

    print("=" * 55)
    print("  Patient Outreach System - Automated Test Suite")
    print("=" * 55)

    print("\n[1] HTML Page Routes")
    test_route("/")
    test_route("/patients")
    test_route("/patients/1")
    test_route("/patients/2")
    test_route("/outreach")
    test_route("/escalations")
    test_route("/reviews")
    test_route("/reports")

    print("\n[2] JSON API - Read Endpoints")
    test_route("/api/patients")
    test_route("/api/patients/1")
    test_route("/api/patients/9999", expected_status=404)
    test_route("/api/dashboard/stats")
    test_route("/api/patients/1/explain")
    test_route("/api/patients/1/generate-plan")
    test_route("/api/patients/4/explain")

    print("\n[3] JSON API - Write Endpoints")
    test_route(
        "/api/outreach/1/status",
        method="POST",
        post_data={"status": "Contacted", "notes": "Patient answered"},
    )
    test_route(
        "/api/patients/1/review",
        method="POST",
        post_data={
            "reviewer_name": "Dr. Test Clinician",
            "review_status": "Approved",
            "comments": "Plan is appropriate.",
            "approved_plan": "Schedule diabetes review within 2 weeks.",
        },
    )
    test_route(
        "/api/patients/4/escalate",
        method="POST",
        post_data={
            "reason": "HbA1c critically elevated; patient lives alone.",
            "urgency": "Urgent",
            "assigned_to": "Dr. Sarah Malik (Lead GP)",
        },
    )
    # PATCH test using http.client directly
    try:
        conn = http.client.HTTPConnection("127.0.0.1", 8789)
        conn.request("PATCH", "/api/escalations/1/resolve?resolution=Appointment+booked")
        resp = conn.getresponse()
        resp.read()
        if resp.status == 200:
            PASSED = PASSED + 1
            print("  PASS  PATCH   /api/escalations/1/resolve -> 200")
        else:
            FAILED = FAILED + 1
            print(f"  FAIL  PATCH   /api/escalations/1/resolve -> {resp.status}")
        conn.close()
    except Exception as e:
        FAILED = FAILED + 1
        print(f"  FAIL  PATCH   /api/escalations/1/resolve -> ERROR: {e}")

    print("\n[4] Agent Logic Tests")
    req = urllib.request.Request(BASE + "/api/patients/1/explain")
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read())
    ok = "explanation" in data and "Margaret Thompson" in data["explanation"] and len(data["explanation"]) > 200
    if ok:
        PASSED = PASSED + 1
        print("  PASS  AI explanation contains patient name and sufficient content")
    else:
        FAILED = FAILED + 1
        print("  FAIL  AI explanation missing expected content")

    req = urllib.request.Request(BASE + "/api/patients/1/generate-plan")
    with urllib.request.urlopen(req, timeout=5) as r:
        plan = json.loads(r.read())
    keys_ok = all(k in plan for k in ("contact_method", "next_step", "responsible_role", "follow_up_date", "rationale"))
    if keys_ok:
        PASSED = PASSED + 1
        print("  PASS  Outreach plan contains all required fields")
    else:
        FAILED = FAILED + 1
        print("  FAIL  Outreach plan missing fields")

    req = urllib.request.Request(BASE + "/api/dashboard/stats")
    with urllib.request.urlopen(req, timeout=5) as r:
        stats = json.loads(r.read())
    if stats["total_patients"] == 10:
        PASSED = PASSED + 1
        print(f"  PASS  Dashboard stats: {stats['total_patients']} patients, risk={stats['risk_distribution']}")
    else:
        FAILED = FAILED + 1
        print(f"  FAIL  Expected 10 patients, got {stats['total_patients']}")

    total = PASSED + FAILED
    print()
    print("=" * 55)
    print(f"  RESULTS: {PASSED}/{total} passed  {'ALL PASSED' if FAILED == 0 else str(FAILED) + ' FAILED'}")
    print("=" * 55)

    if FAILED > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
