"""
Migration: Create and seed the service_charter table.
Run this once from the backend directory:
    python migrate_service_charter.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import engine, SessionLocal
from models import Base, ServiceCharter

# ── Create the table if it doesn't exist ──────────────────────────────────────
Base.metadata.create_all(bind=engine, tables=[ServiceCharter.__table__])
print("✅  service_charter table created (or already exists).")

# ── Seed data ─────────────────────────────────────────────────────────────────
CHARTER_DATA = [
    (1,  "ICT Helpdesk Support",                  "Call, written request, helpdesk ticket, email, or walk-in",              "Nil",           "Within 48 hours"),
    (2,  "Network/Email Restoration",              "Written request, call, or system detection",                             "Nil",           "Within 24 hours"),
    (3,  "ICT Training (Students & Staff)",        "Written request, identification of training needs",                     "Nil",           "Within 2 weeks"),
    (4,  "Security Breach Resolution",             "Detection via monitoring system",                                        "Nil",           "Within 48 hours"),
    (5,  "New User Account Creation (Email/ERP)",  "Written request",                                                        "Nil",           "Within 24 hours"),
    (6,  "Password Reset",                         "Call or helpdesk ticket",                                                "Nil",           "Within 24 hours"),
    (7,  "ICT Equipment Maintenance & Repairs",    "Maintenance schedule, warranty status",                                  "Nil",           "Within 4 weeks"),
    (8,  "Escalation of Equipment Faults",         "Diagnosis report, request for parts/quotation",                         "Per quotation", "Within 7 days"),
    (9,  "Mini Website Development",               "Written request, content, and specifications",                           "Nil",           "Within 1 month"),
    (10, "Project Implementation",                 "Requirements, proposal/plan, procurement procedure",                    "Nil",           "1 year before tender award"),
    (11, "ICT Equipment Specifications",           "Written request",                                                        "Nil",           "Within 48 hours"),
    (12, "Response to ICT Queries",                "Written request, email, or call",                                        "Nil",           "Within 24 hours"),
    (13, "Computer Lab Services",                  "Written request",                                                        "Nil",           "Working days"),
    (14, "Website Updates",                        "Written request or email",                                               "Nil",           "Within 24 hours"),
    (15, "New Website Design",                     "Written request or email",                                               "Nil",           "Within 1 month"),
]

db = SessionLocal()
inserted = 0
skipped = 0

try:
    for num, name, reqs, charges, timeline in CHARTER_DATA:
        existing = db.query(ServiceCharter).filter(ServiceCharter.service_number == num).first()
        if existing:
            skipped += 1
            continue
        entry = ServiceCharter(
            service_number=num,
            service_name=name,
            requirements=reqs,
            charges=charges,
            timelines=timeline
        )
        db.add(entry)
        inserted += 1

    db.commit()
    print(f"✅  Seeded {inserted} service charter entries ({skipped} already existed).")
except Exception as e:
    db.rollback()
    print(f"❌  Error seeding data: {e}")
finally:
    db.close()
