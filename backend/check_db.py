from database import SessionLocal
from models import Department, Feedback

def check_data():
    db = SessionLocal()
    try:
        print("--- Departments ---")
        depts = db.query(Department).all()
        for d in depts:
            print(f"ID: {d.id}, Name: {d.name}")
        
        print("\n--- Recent Feedback ---")
        feedbacks = db.query(Feedback).order_by(Feedback.id.desc()).limit(5).all()
        for f in feedbacks:
            print(f"ID: {f.id}, Tracking: {f.tracking_id}, DeptID: {f.department_id}, Office: {f.office}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
