import sys
import os

# Add the parent directory to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from models import User, Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_initial_admin():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if any admin exists
        admin_exists = db.query(User).filter(User.role == "admin").first()
        if admin_exists:
            print(f"Admin already exists: {admin_exists.email}")
            return

        print("Creating initial admin user...")
        email = os.getenv("ADMIN_EMAIL", "admin@seku.ac.ke")
        password = os.getenv("ADMIN_PASSWORD", "admin123")
        fullname = os.getenv("ADMIN_NAME", "System Administrator")

        hashed_password = pwd_context.hash(password)
        
        new_admin = User(
            fullname=fullname,
            email=email,
            hashed_password=hashed_password,
            role="admin"
        )
        
        db.add(new_admin)
        db.commit()
        print(f"Successfully created admin: {email}")
        print(f"Password: {password}")
        
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_admin()