from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
import bcrypt
from datetime import datetime

# Direct connection to avoid any other import issues
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Aaamumo254%@localhost/feedback_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_password_hash(password: str) -> str:
    # Use bcrypt directly to avoid passlib-bcrypt 4.x incompatibility
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_complaint_admins():
    db = SessionLocal()
    try:
        password = "aaamumo254"
        hashed_pw = get_password_hash(password)
        
        admins = [
            {"username": "complain1", "fullname": "Complaint Manager 1", "email": "complain1@seku.ac.ke"},
            {"username": "complain2", "fullname": "Complaint Manager 2", "email": "complain2@seku.ac.ke"}
        ]
        
        for admin in admins:
            exists = db.query(User).filter((User.username == admin["username"]) | (User.email == admin["email"])).first()
            if not exists:
                new_user = User(
                    fullname=admin["fullname"],
                    username=admin["username"],
                    email=admin["email"],
                    hashed_password=hashed_pw,
                    role="admin",
                    department_id=None,
                    created_at=datetime.utcnow()
                )
                db.add(new_user)
                print(f"✅ Created {admin['username']}")
            else:
                print(f"ℹ️ Admin {admin['username']} already exists")
        
        db.commit()
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_complaint_admins()
