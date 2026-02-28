"""
seed.py  –  AI-MEDX 2K26
─────────────────────────────────────────────────────────────────────────────
ADD YOUR STUDENTS HERE, then run:

    python seed.py

Each entry:  ("Full Name", "Department", "PhoneNumber", "Token6Digits")
─────────────────────────────────────────────────────────────────────────────
"""

from app import app, db
from models import Student

# ══════════════════════════════════════════════════════════════════════════════
#  ▼▼▼  ENTER YOUR STUDENTS HERE  ▼▼▼
# ══════════════════════════════════════════════════════════════════════════════

STUDENTS = [
    # ( Name,              Department,  Phone,        Token  )
    ("S. Saravanan",       "AI&DS",     "9000000001", "100001"),
    ("A. Anitha",          "AI&DS",     "9000000002", "100002"),
    ("R. Rajesh",          "CSE",       "9000000003", "100003"),
    ("M. Meena",           "ECE",       "9000000004", "100004"),
    ("K. Karthik",         "MECH",      "9000000005", "100005"),
    # ── Add more rows below ──────────────────────────────────
    # ("Name",  "Dept",  "Phone",  "Token"),
]

# ══════════════════════════════════════════════════════════════════════════════
#  ▲▲▲  DO NOT EDIT BELOW THIS LINE  ▲▲▲
# ══════════════════════════════════════════════════════════════════════════════

def seed():
    with app.app_context():
        db.create_all()
        added = 0
        skipped = 0
        for name, dept, phone, token in STUDENTS:
            if Student.query.filter_by(phone=phone).first():
                print(f"  [SKIP]  {name} ({phone}) — already exists")
                skipped += 1
            else:
                db.session.add(Student(name=name, dept=dept, phone=phone, token=token))
                print(f"  [ADD]   {name} ({phone})  →  Token: {token}")
                added += 1
        db.session.commit()
        print(f"\n  Done! Added: {added}  |  Skipped: {skipped}")

if __name__ == "__main__":
    seed()
