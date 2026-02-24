import sys
import os

# Add the current directory to sys.path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from models import Base, Department, User, Feedback, ActivityLog
from database import SQLALCHEMY_DATABASE_URL

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Initialize database connection
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrate_and_seed():
    db = SessionLocal()
    try:
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        print("Creating new tables...")
        Base.metadata.create_all(bind=engine)
        
        departments_list = [
            "Administration", "Library", "Finance", "Admissions", 
            "ICT", "Security", "Catering", "Registry", 
            "Health Unit", "Games & Sports", "Hostel", "Dean of Students"
        ]
        
        print(f"Seeding {len(departments_list)} departments...")
        dept_objects = {}
        for dept_name in departments_list:
            dept = Department(name=dept_name)
            db.add(dept)
            db.flush() # Get ID
            dept_objects[dept_name] = dept.id
        
        db.commit()
        print("Departments seeded successfully.")
        
        common_password = get_password_hash("aaamumo254")
        
        print("Seeding admin accounts...")
        for dept_name, dept_id in dept_objects.items():
            # Create two admins per department
            username_base = dept_name.lower().replace(" ", "").replace("&", "")
            
            for i in range(1, 3):
                username = f"{username_base}{i}"
                admin_user = User(
                    fullname=f"{dept_name} Admin {i}",
                    username=username,
                    email=f"{username}@university.edu",
                    hashed_password=common_password,
                    role="admin",
                    department_id=dept_id
                )
                db.add(admin_user)
        
        db.commit()
        print("Admin accounts seeded successfully.")
        
        print("✅ Migration and seeding completed!")
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_and_seed()
