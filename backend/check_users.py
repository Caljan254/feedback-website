from database import SessionLocal
from models import User, Department

def check_users():
    db = SessionLocal()
    try:
        print("--- Admins ---")
        admins = db.query(User).filter(User.role == "admin").all()
        for a in admins:
            print(f"ID: {a.id}, Email: {a.email}, DeptID: {a.department_id}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
