from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Feedback, User, Department, ActivityLog
from schemas import (
    FeedbackCreate, FeedbackOut, UserCreate, UserOut, 
    LoginRequest, Token, FeedbackTrackRequest
)
from auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from database import get_db
from datetime import datetime
from typing import List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 🧾 Register Route
@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Registration attempt for email: {user.email}")
        
        # Check if user exists
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            logger.warning(f"Email already registered: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # First user becomes admin
        user_count = db.query(User).count()
        is_first_user = user_count == 0
        role = "admin" if is_first_user else user.role
        
        logger.info(f"User count: {user_count}, Is first user: {is_first_user}, Assigned role: {role}")

        # Hash password
        hashed_password = get_password_hash(user.password)
        
        # Create new user
        new_user = User(
            fullname=user.fullname,
            email=user.email,
            hashed_password=hashed_password,
            role=role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User registered successfully: {user.email} with role {role}")
        return new_user
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in register: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in register: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# 👤 Login Route
@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Login attempt for {request.email or request.username}")
        
        # Authenticate user
        user = authenticate_user(
            db, 
            email=request.email, 
            username=request.username, 
            password=request.password
        )
        if not user:
            logger.warning(f"Invalid credentials for {request.email or request.username}")
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # Create access token
        access_token = create_access_token(data={"sub": user.email or user.username})
        
        logger.info(f"User logged in successfully: {user.email or user.username} with role {user.role}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role,
            "email": user.email,
            "username": user.username,
            "fullname": user.fullname,
            "department_id": user.department_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# 💬 Submit Feedback Route
@router.post("/submit-feedback", response_model=FeedbackOut)
def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db), 
                   current_user: User = Depends(get_current_user)):
    try:
        # Convert to dict
        feedback_dict = feedback.dict()
        
        # If user is authenticated, use their email
        if current_user:
            feedback_dict['email'] = current_user.email
            feedback_dict['name'] = feedback_dict.get('name') or current_user.fullname
        
        # If department_id is not provided, try to find it by office name
        if not feedback_dict.get('department_id') and feedback_dict.get('office'):
            office_val = feedback_dict['office'].lower()
            # Mapping frontend slugs to DB names
            slug_map = {
                'vc-office': "Vice Chancellor's Office",
                'dvc-academic': "DVC (Academic, Research & Student Affairs)",
                'dvc-admin': "DVC (Administration, Finance & Planning)",
                'registrar-academic': "Registrar (Academic Affairs)",
                'registrar-admin': "Registrar (Administration & Human Resource)",
                'council-office': "University Council Office",
                'legal-services': "Legal Services Office",
                'corp-comm': "Corporate Communications / PR",
                'admissions': "Admissions Office",
                'academic-registry': "Academic Registry",
                'exams-office': "Examinations Office",
                'timetabling': "Timetabling Office",
                'research-postgrad': "Research, Innovation & Postgraduate Studies",
                'quality-assurance': "Quality Assurance Office",
                'industrial-attachment': "Industrial Attachment & Career Services",
                'elearning': "e-Learning / ODL Office",
                'ssc-dean': "Dean, School of Science and Computing",
                'dept-math': "Department of Mathematics",
                'dept-ict': "Department of Computing & IT",
                'dept-physical': "Department of Physical Sciences",
                'dept-biological': "Department of Biological Sciences",
                'set-dean': "Dean, School of Engineering",
                'dept-civil': "Department of Civil Engineering",
                'dept-elec': "Department of Electrical & Electronic Engineering",
                'dept-mech': "Department of Mechanical Engineering",
                'sbe-dean': "Dean, School of Business",
                'dept-admin': "Department of Business Administration",
                'dept-accounting': "Department of Accounting & Finance",
                'dept-economics': "Department of Economics",
                'seh-dean': "Dean, School of Education",
                'dept-edu': "Department of Educational Studies",
                'dept-social': "Department of Social Sciences",
                'dept-humanities': "Department of Humanities",
                'sanr-dean': "Dean, School of Agriculture",
                'dept-env': "Department of Environmental Science",
                'dept-agri': "Department of Agricultural Sciences",
                'dean-students': "Dean of Students Office",
                'student-affairs': "Student Affairs Office",
                'counselling': "Counselling Services",
                'chaplaincy': "Chaplaincy / Spiritual Services",
                'career-guidance': "Career Guidance Office",
                'games': "Games and Sports Office",
                'student-clubs': "Student Clubs & Associations Office",
                'finance': "Finance Department",
                'fees-office': "Fees Office",
                'accounts-office': "Accounts Office",
                'procurement': "Procurement Office",
                'internal-audit': "Internal Audit Office",
                'hr-office': "Human Resource Office",
                'staff-welfare': "Staff Welfare Office",
                'training-dev': "Training & Development Office",
                'library': "Library Services",
                'ict-services': "ICT Services",
                'health-unit': "Health Unit / Clinic",
                'hostel': "Accommodation / Hostel Office",
                'catering': "Catering Services",
                'estate': "Estate / Maintenance Department",
                'transport': "Transport Office",
                'security': "Security Department",
                'grounds': "Grounds & Cleaning Services",
                'research-dir': "Research Directorate",
                'innovation-office': "Innovation & Tech Transfer Office",
                'community-outreach': "Community Outreach & Extension"
            }
            dept_name = slug_map.get(office_val, office_val)
            dept = db.query(Department).filter(Department.name.ilike(dept_name)).first()
            if dept:
                feedback_dict['department_id'] = dept.id

        # Set default values for status fields
        feedback_dict['is_read'] = False
        feedback_dict['read_at'] = None
        feedback_dict['replied_at'] = None
        feedback_dict['reply_message'] = None
        
        # Generate a unique tracking ID
        import secrets
        import string
        alphabet = string.ascii_uppercase + string.digits
        tracking_id = ''.join(secrets.choice(alphabet) for _ in range(10))
        feedback_dict['tracking_id'] = f"REF-{tracking_id}"
        
        db_feedback = Feedback(**feedback_dict)
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        logger.info(f"Feedback submitted: ID {db_feedback.id}, Tracking ID {db_feedback.tracking_id}")
        return db_feedback
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in submit_feedback: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

# 👀 Admin Route – View All Feedback
@router.get("/admin/feedback", response_model=List[FeedbackOut])
def get_all_feedback(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        if current_user.role != "admin":
            logger.warning(f"Non-admin {current_user.email} attempted to access admin feedback")
            raise HTTPException(status_code=403, detail="Forbidden – Admins only")
        
        logger.info(f"Admin {current_user.email or current_user.username} fetching feedback")
        
        query = db.query(Feedback)
        if current_user.role == "admin" and current_user.department_id:
            query = query.filter(Feedback.department_id == current_user.department_id)
            
        feedback = query.order_by(Feedback.created_at.desc()).all()
        logger.info(f"Returning {len(feedback)} feedback entries")
        return feedback
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_all_feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

# ✅ Mark feedback as read
@router.post("/admin/feedback/{feedback_id}/read")
def mark_feedback_as_read(
    feedback_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        if not current_user or current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden – Admins only")
        
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        if feedback.department_id != current_user.department_id:
             raise HTTPException(status_code=403, detail="Forbidden – Not your department")

        feedback.is_read = True
        feedback.read_at = datetime.now()
        
        # Log action
        log = ActivityLog(
            user_id=current_user.id,
            department_id=current_user.department_id,
            action="read_message",
            details=f"Marked feedback ID {feedback_id} as read"
        )
        db.add(log)
        db.commit()
        
        logger.info(f"Feedback {feedback_id} marked as read by admin {user_id_for_log(current_user)}")
        return {"message": "Feedback marked as read", "status": "read"}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in mark_as_read: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

# ✅ Mark feedback as answered
@router.post("/admin/feedback/{feedback_id}/answered")
def mark_feedback_as_answered(
    feedback_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        if not current_user or current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden – Admins only")
        
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        if feedback.department_id != current_user.department_id:
             raise HTTPException(status_code=403, detail="Forbidden – Not your department")

        feedback.replied_at = datetime.now()
        
        # Log action
        log = ActivityLog(
            user_id=current_user.id,
            department_id=current_user.department_id,
            action="mark_answered",
            details=f"Marked feedback ID {feedback_id} as answered manually"
        )
        db.add(log)
        db.commit()
        
        logger.info(f"Feedback {feedback_id} marked as answered by admin {user_id_for_log(current_user)}")
        return {"message": "Feedback marked as answered", "status": "answered"}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in mark_as_answered: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

# 📧 Send Reply Route
@router.post("/send-reply")
def send_reply(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if not current_user or current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden – Admins only")

        email = request.get("email")
        subject = request.get("subject")
        message = request.get("message")
        feedback_id = request.get("feedback_id")

        if not email or not subject or not message or not feedback_id:
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Update feedback with reply info
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
            
        if feedback.department_id != current_user.department_id:
             raise HTTPException(status_code=403, detail="Forbidden – Not your department")

        feedback.replied_at = datetime.now()
        feedback.reply_message = message
        feedback.is_read = True
        feedback.read_at = datetime.now()
        
        # Log action
        log = ActivityLog(
            user_id=current_user.id,
            department_id=current_user.department_id,
            action="reply_message",
            details=f"Sent reply to feedback ID {feedback_id}"
        )
        db.add(log)
        db.commit()
        
        logger.info(f"Reply sent to feedback {feedback_id} by admin {user_id_for_log(current_user)}")
        
        return {"message": "✅ Reply sent successfully and feedback marked as answered"}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in send_reply: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

# 👤 User Route – View Own Feedback
@router.get("/user/feedback", response_model=List[FeedbackOut])
def get_user_feedback(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        logger.info(f"User {current_user.email} fetching their feedback")
        feedback = db.query(Feedback).filter(Feedback.email == current_user.email).order_by(Feedback.created_at.desc()).all()
        logger.info(f"Returning {len(feedback)} feedback entries for user {current_user.email}")
        return feedback
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

# 👤 Anonymous Route – Track Feedback by Email or Tracking ID
@router.post("/feedback/track", response_model=List[FeedbackOut])
def track_feedback(request: FeedbackTrackRequest, db: Session = Depends(get_db)):
    try:
        if not request.email and not request.tracking_id:
            raise HTTPException(status_code=400, detail="Email or Tracking ID required")
            
        query = db.query(Feedback)
        if request.tracking_id:
            logger.info(f"Tracking feedback for ID: {request.tracking_id}")
            feedback = query.filter(Feedback.tracking_id == request.tracking_id).all()
        else:
            logger.info(f"Tracking feedback for email: {request.email}")
            feedback = query.filter(Feedback.email == request.email).order_by(Feedback.created_at.desc()).all()
            
        logger.info(f"Returning {len(feedback)} feedback entries")
        return feedback
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in track_feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

# 👤 Get single feedback
@router.get("/user/feedback/{feedback_id}", response_model=FeedbackOut)
def get_single_user_feedback(
    feedback_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        feedback = db.query(Feedback).filter(
            Feedback.id == feedback_id, 
            Feedback.email == current_user.email
        ).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return feedback
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_single_user_feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

# 👤 Mark feedback as read (user)
@router.post("/user/feedback/{feedback_id}/read")
def mark_user_feedback_as_read(
    feedback_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        feedback = db.query(Feedback).filter(
            Feedback.id == feedback_id, 
            Feedback.email == current_user.email
        ).first()
        
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        feedback.is_read = True
        feedback.read_at = datetime.now()
        db.commit()
        
        logger.info(f"Feedback {feedback_id} marked as read by user {current_user.email}")
        return {"message": "Feedback marked as read"}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in mark_user_feedback_as_read: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

# 🏢 Get Departments List
@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()

# 📋 Activity Logs
@router.get("/admin/activity-logs")
def get_activity_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    return db.query(ActivityLog).filter(
        ActivityLog.department_id == current_user.department_id
    ).order_by(ActivityLog.timestamp.desc()).limit(50).all()

# 📥 Export CSV
@router.get("/admin/export-csv")
def export_feedback_csv(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    import csv
    import io
    from fastapi.responses import StreamingResponse

    feedback = db.query(Feedback).filter(
        Feedback.department_id == current_user.department_id
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Email", "Message", "Rating", "Created At", "Status"])
    
    for f in feedback:
        status = "Replied" if f.replied_at else ("Read" if f.is_read else "Unread")
        writer.writerow([f.id, f.name, f.email, f.message, f.rating, f.created_at, status])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=feedback_dept_{current_user.department_id}.csv"}
    )

# 🔐 Get Current User Info
@router.get("/user/me")
def get_user_profile(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    return {
        "id": current_user.id,
        "fullname": current_user.fullname,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "department_id": current_user.department_id,
        "created_at": current_user.created_at
    }

def user_id_for_log(user):
    return user.username or user.email or str(user.id)
