from database import SessionLocal
from models import User, Department

def check_users():
    db = SessionLocal()
    try:
        print("--- Admins Directorate Of ICT  ---")
        ict_dept = db.query(Department).filter(Department.name == "Directorate Of ICT").first()
        if ict_dept:
            print(f"Dept Name: {ict_dept.name}, ID: {ict_dept.id}")
            admins = db.query(User).filter(User.department_id == ict_dept.id).all()
            for a in admins:
                print(f"Admin ID: {a.id}, Email: {a.email}, Name: {a.fullname}")
        else:
            print("Directorate Of ICT department not found!")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
