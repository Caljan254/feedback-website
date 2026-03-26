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
        
        # Specific mapping of Office Name -> Username Prefix
        admin_mapping = {
            "Vice Chancellor's Office": "vc",
            "Deputy Vice Chancellor (Academic)": "dvcaa",
            "Deputy Vice Chancellor (Administration)": "dvcaf",
            "Registrar (Academic Affairs)": "regacad",
            "Registrar (Administration & HR)": "regadmin",
            "University Council Office": "council",
            "Legal Services Office": "legal",
            "Corporate Communications": "pr",
            "Admissions Office": "admissions",
            "Academic Registry": "registry",
            "Examinations Office": "exams",
            "Timetabling Office": "timetable",
            "Research Directorate": "research",
            "Quality Assurance": "quality",
            "Attachment & Career Services": "career",
            "e-Learning Office": "elearning",
            "School of Science & Computing - Dean's Office": "scideans",
            "Mathematics Department (Chairperson)": "math",
            "Computing & IT Department": "cit",
            "Physical Sciences": "physics",
            "Biological Sciences": "bio",
            "School of Engineering - Dean's Office": "engdean",
            "Civil Engineering": "civil",
            "Electrical Engineering": "electrical",
            "Mechanical Engineering": "mech",
            "School of Business - Dean's Office": "busdean",
            "Business Administration": "ba",
            "Accounting & Finance": "accfin",
            "Economics": "econ",
            "School of Education & Social Sciences - Dean's Office": "edudean",
            "Educational Studies": "edu",
            "Social Sciences": "socialsci",
            "Humanities": "humanities",
            "School of Agriculture & Environment - Dean's Office": "agrideans",
            "Environmental Science": "env",
            "Agricultural Sciences": "agri",
            "Dean of Students": "dean",
            "Student Affairs": "students",
            "Counselling Services": "counselling",
            "Chaplaincy": "chaplain",
            "Games & Sports": "sports",
            "Student Clubs": "clubs",
            "Finance Department": "finance",
            "Fees Office": "fees",
            "Accounts Office": "accounts",
            "Procurement Office": "procurement",
            "Internal Audit": "audit",
            "Human Resource": "hr",
            "Staff Welfare": "welfare",
            "Training & Development": "training",
            "Library": "library",
            "Directorate Of ICT": "ict",
            "Health Unit": "health",
            "Hostel / Accommodation": "hostel",
            "Catering": "catering",
            "Estate / Maintenance": "estate",
            "Transport": "transport",
            "Security": "security",
            "Grounds & Cleaning": "grounds",
            "Innovation Office": "innovation",
            "Community Outreach": "outreach"
        }
        
        print(f"Seeding {len(admin_mapping)} departments...")
        dept_objects = {}
        for dept_name in admin_mapping.keys():
            dept = Department(name=dept_name)
            db.add(dept)
            db.flush() # Get ID
            dept_objects[dept_name] = dept.id
        
        db.commit()
        print("Departments seeded successfully.")
        
        common_password = get_password_hash("aaamumo254")
        
        print("Seeding admin accounts...")
        for dept_name, username_prefix in admin_mapping.items():
            dept_id = dept_objects[dept_name]
            # Create two admins per department
            for i in range(1, 3):
                username = f"{username_prefix}{i}"
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
        print("[OK] Migration and seeding completed!")
        
    except Exception as e:
        print(f"[ERROR] Error during migration: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_and_seed()
