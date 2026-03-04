from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Feedback, User, Department, ActivityLog, Question, QuestionResponse
from schemas import (
    FeedbackCreate, FeedbackOut, UserCreate, UserOut, 
    LoginRequest, Token, FeedbackTrackRequest,
    QuestionCreate, QuestionOut, QuestionResponseCreate, FeedbackCreateExtended,
    FeedbackOutExtended
)
from auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from database import get_db
from datetime import datetime
from typing import List, Optional
import logging
from email_service import email_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dependency Helper for Background Notifications
def notify_admins_task(feedback_id: int):
    """Background task to send email notifications to admins without delaying the user."""
    from database import SessionLocal
    db = SessionLocal()
    try:
        db_feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not db_feedback or not db_feedback.department_id:
            return

        admins = db.query(User).filter(
            User.department_id == db_feedback.department_id,
            User.role == "admin"
        ).all()
        
        dept = db.query(Department).filter(Department.id == db_feedback.department_id).first()
        dept_name = dept.name if dept else db_feedback.office
        
        for admin in admins:
            if admin.email:
                email_service.send_new_feedback_notification(
                    to_email=admin.email,
                    department_name=dept_name,
                    feedback_data={
                        "name": db_feedback.name or "Anonymous",
                        "email": db_feedback.email or "N/A",
                        "rating": db_feedback.rating or "N/A",
                        "message": db_feedback.message or "No message provided.",
                        "tracking_id": db_feedback.tracking_id
                    }
                )
    except Exception as e:
        logger.error(f"Error in notify_admins_task: {str(e)}")
    finally:
        db.close()

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
def submit_feedback(feedback: FeedbackCreateExtended, background_tasks: BackgroundTasks, 
                    db: Session = Depends(get_db), 
                    current_user: User = Depends(get_current_user)):
    try:
        # Convert to dict
        feedback_dict = feedback.dict()
        dynamic_responses = feedback_dict.pop('dynamic_responses', [])
        
        # If user is authenticated, use their email
        if current_user:
            feedback_dict['email'] = current_user.email
            feedback_dict['name'] = feedback_dict.get('name') or current_user.fullname
        
        # If department_id is not provided, try to find it by office name
        if not feedback_dict.get('department_id') and feedback_dict.get('office'):
            office_val = feedback_dict['office'].lower()
            # Mapping frontend slugs to DB names
            slug_map = {
                'vc-office': "Vice Chancellor’s Office",
                'dvc-academic': "Deputy Vice Chancellor (Academic)",
                'dvc-admin': "Deputy Vice Chancellor (Administration)",
                'registrar-academic': "Registrar (Academic Affairs)",
                'registrar-admin': "Registrar (Administration & HR)",
                'council-office': "University Council Office",
                'legal-services': "Legal Services Office",
                'corp-comm': "Corporate Communications",
                'admissions': "Admissions Office",
                'academic-registry': "Academic Registry",
                'exams-office': "Examinations Office",
                'timetabling': "Timetabling Office",
                'research-postgrad': "Research Directorate",
                'quality-assurance': "Quality Assurance",
                'industrial-attachment': "Attachment & Career Services",
                'elearning': "e-Learning Office",
                'ssc-dean': "School of Science & Computing - Dean’s Office",
                'dept-math': "Mathematics Department (Chairperson)",
                'dept-ict': "Computing & IT Department",
                'dept-physical': "Physical Sciences",
                'dept-biological': "Biological Sciences",
                'set-dean': "School of Engineering - Dean’s Office",
                'dept-civil': "Civil Engineering",
                'dept-elec': "Electrical Engineering",
                'dept-mech': "Mechanical Engineering",
                'sbe-dean': "School of Business - Dean’s Office",
                'dept-admin': "Business Administration",
                'dept-accounting': "Accounting & Finance",
                'dept-economics': "Economics",
                'seh-dean': "School of Education & Social Sciences - Dean’s Office",
                'dept-edu': "Educational Studies",
                'dept-social': "Social Sciences",
                'dept-humanities': "Humanities",
                'sanr-dean': "School of Agriculture & Environment - Dean’s Office",
                'dept-env': "Environmental Science",
                'dept-agri': "Agricultural Sciences",
                'dean-students': "Dean of Students",
                'student-affairs': "Student Affairs",
                'counselling': "Counselling Services",
                'chaplaincy': "Chaplaincy",
                'career-guidance': "Attachment & Career Services",
                'games': "Games & Sports",
                'student-clubs': "Student Clubs",
                'finance': "Finance Department",
                'fees-office': "Fees Office",
                'accounts-office': "Accounts Office",
                'procurement': "Procurement Office",
                'internal-audit': "Internal Audit",
                'hr-office': "Human Resource",
                'staff-welfare': "Staff Welfare",
                'training-dev': "Training & Development",
                'library': "Library",
                'ict-services': "ICT Services",
                'health-unit': "Health Unit",
                'hostel': "Hostel / Accommodation",
                'catering': "Catering",
                'estate': "Estate / Maintenance",
                'transport': "Transport",
                'security': "Security",
                'grounds': "Grounds & Cleaning",
                'research-dir': "Research Directorate",
                'innovation-office': "Innovation Office",
                'community-outreach': "Community Outreach"
            }
            dept_name = slug_map.get(office_val, office_val)
            # Handle different apostrophes (straight vs curly)
            dept_name_alt = dept_name.replace("’", "'") if "’" in dept_name else dept_name.replace("'", "’")
            
            dept = db.query(Department).filter(
                (Department.name.ilike(dept_name)) | (Department.name.ilike(dept_name_alt))
            ).first()
            
            if dept:
                feedback_dict['department_id'] = dept.id
                logger.info(f"Mapped office '{office_val}' to department '{dept.name}' (ID: {dept.id})")
            else:
                logger.warning(f"Could not map office '{office_val}' to any department. Dept name searched: '{dept_name}'")

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
        
        # Filter feedback_dict to only include keys that exist in the Feedback model
        allowed_keys = {c.key for c in Feedback.__table__.columns}
        filtered_feedback_dict = {k: v for k, v in feedback_dict.items() if k in allowed_keys}
        
        db_feedback = Feedback(**filtered_feedback_dict)
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)

        # Save dynamic responses
        for resp in dynamic_responses:
            db_resp = QuestionResponse(
                feedback_id=db_feedback.id,
                question_id=resp['question_id'],
                answer=resp['answer']
            )
            db.add(db_resp)
        
        if dynamic_responses:
            db.commit()
        
        logger.info(f"Feedback submitted: ID {db_feedback.id}, Tracking ID {db_feedback.tracking_id}, Dept ID {db_feedback.department_id}")

        # Trigger notification in background to speed up response for the user
        if db_feedback.department_id:
            background_tasks.add_task(notify_admins_task, db_feedback.id)
            logger.info(f"Background notification task scheduled for feedback ID: {db_feedback.id}")

        return db_feedback
        
    except SQLAlchemyError as e:
        import traceback
        error_msg = str(e)
        stack_trace = traceback.format_exc()
        logger.error(f"Database error in submit_feedback: {error_msg}\n{stack_trace}")
        print(f"❌ DATABASE ERROR: {error_msg}")
        print(f"DATA ATTEMPTED: {feedback_dict}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {error_msg[:100]}")

# 👀 Admin Route – View All Feedback
@router.get("/admin/feedback", response_model=List[FeedbackOutExtended])
def get_all_feedback(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        if current_user.role != "admin":
            logger.warning(f"Non-admin {current_user.email} attempted to access admin feedback")
            raise HTTPException(status_code=403, detail="Forbidden – Admins only")
        
        logger.info(f"Admin {current_user.email or current_user.username} fetching feedback")
        
        # We use joinedload or simply rely on relationship lazy loading which Pydantic handles
        query = db.query(Feedback)
        if current_user.role == "admin" and current_user.department_id:
            query = query.filter(Feedback.department_id == current_user.department_id)
            
        feedback = query.order_by(Feedback.created_at.desc()).all()
        
        # For each feedback, we need to populate question_text in responses if we want it in the UI
        # But let's keep it simple for now, the UI can fetch questions separately or we can map them here.
        
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
        
        if current_user.department_id and feedback.department_id != current_user.department_id:
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
        
        if current_user.department_id and feedback.department_id != current_user.department_id:
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

        if not message or not feedback_id:
            raise HTTPException(status_code=400, detail="Missing required fields: message and feedback_id")

        # Update feedback with reply info
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
            
        if current_user.department_id and feedback.department_id != current_user.department_id:
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
        
        # Send email notification if user has an email
        if feedback.email:
            try:
                email_sent = email_service.send_feedback_reply(
                    to_email=feedback.email,
                    subject=subject or f"Response to your feedback regarding {feedback.office}",
                    message=message,
                    user_name=feedback.name
                )
                if email_sent:
                    logger.info(f"Email notification sent to {feedback.email}")
                else:
                    logger.error(f"Failed to send email notification to {feedback.email}")
            except Exception as e:
                logger.error(f"Error calling email service: {str(e)}")

        return {"message": "✅ Reply sent successfully and feedback marked as answered"}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in send_reply: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

# 📨 Admin → Member: Send proactive message to registered user
@router.post("/admin/send-message")
def send_admin_message_to_member(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if not current_user or current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden – Admins only")

        recipient_email = request.get("recipient_email", "").strip()
        subject = request.get("subject", "").strip()
        message = request.get("message", "").strip()

        if not recipient_email or not message:
            raise HTTPException(status_code=400, detail="recipient_email and message are required")

        # Verify the recipient is a registered member
        recipient = db.query(User).filter(User.email == recipient_email).first()
        if not recipient:
            raise HTTPException(status_code=404, detail=f"No registered member found with email: {recipient_email}")

        # Create a feedback record as the "admin message" so it appears in My Feedback
        import secrets, string
        alphabet = string.ascii_uppercase + string.digits
        tracking_id = "MSG-" + ''.join(secrets.choice(alphabet) for _ in range(8))

        new_msg = Feedback(
            name=current_user.fullname or "Administration",
            email=recipient_email,
            category="Admin Message",
            office="admin-message",
            message=f"Subject: {subject}\n\n{message}",
            anonymous="false",
            tracking_id=tracking_id,
            department_id=current_user.department_id or feedback.department_id,
            is_read=False,
            reply_message=message,
            replied_at=datetime.now(),   # Mark as already answered since admin composed it
        )
        db.add(new_msg)

        # Log the action
        log = ActivityLog(
            user_id=current_user.id,
            department_id=current_user.department_id,
            action="admin_message",
            details=f"Sent message to {recipient_email}: {subject}"
        )
        db.add(log)
        db.commit()

        logger.info(f"Admin {user_id_for_log(current_user)} sent message to {recipient_email}")
        return {"message": f"✅ Message sent to {recipient_email} successfully"}

    except SQLAlchemyError as e:
        logger.error(f"Database error in send_admin_message: {str(e)}")
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
    
    query = db.query(ActivityLog)
    if current_user.department_id:
        query = query.filter(ActivityLog.department_id == current_user.department_id)
    
    return query.order_by(ActivityLog.timestamp.desc()).limit(50).all()

# 📥 Export CSV
@router.get("/admin/export-csv")
def export_feedback_csv(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    import csv
    import io
    from fastapi.responses import StreamingResponse

    query = db.query(Feedback)
    if current_user.department_id:
        query = query.filter(Feedback.department_id == current_user.department_id)
    
    feedback = query.all()

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

# 🙋‍♂️ Question Management Routes
@router.get("/questions", response_model=List[QuestionOut])
def get_questions(office: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Question).filter(Question.is_active == True)
    if office:
        # Filter by specific office or global (target_office is null)
        query = query.filter((Question.target_office == office) | (Question.target_office == None))
    return query.all()

@router.post("/admin/questions", response_model=QuestionOut)
def add_question(question: QuestionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    db_question = Question(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

@router.delete("/admin/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Soft delete by marking inactive
    db_question.is_active = False
    db.commit()
    return {"message": "Question deleted successfully"}

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
