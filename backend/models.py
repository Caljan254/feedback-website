from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Department(Base):
    __tablename__ = "departments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    
    users = relationship("User", back_populates="department")
    feedbacks = relationship("Feedback", back_populates="department")

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(100), index=True)
    username = Column(String(50), unique=True, index=True, nullable=True) # New for admin accounts
    email = Column(String(100), unique=True, index=True, nullable=True)   # Can be nullable for dept admins
    hashed_password = Column(String(200))
    role = Column(String(20))  # student, staff, visitor, admin
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    department = relationship("Department", back_populates="users")


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)  # Optional if anonymous
    email = Column(String(100), nullable=True)
    category = Column(String(50))  # e.g., 'library', 'ict'
    office = Column(String(100))
    message = Column(Text)
    anonymous = Column(String(5), default="false")  # 'true' or 'false'
    tracking_id = Column(String(20), unique=True, index=True, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    rating = Column(String(50), nullable=True)
    
    # Dynamic question responses
    q_0 = Column(String(50), nullable=True)
    q_1 = Column(String(50), nullable=True)
    q_2 = Column(String(50), nullable=True)
    q_3 = Column(String(50), nullable=True)
    q_4 = Column(String(50), nullable=True)
    
    # Status fields
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    reply_message = Column(Text, nullable=True)

    department = relationship("Department", back_populates="feedbacks")
    responses = relationship("QuestionResponse", back_populates="feedback")


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(500), nullable=False)
    options = Column(String(200), default="Yes,No") # Composed of comma-separated options
    target_office = Column(String(100), nullable=True) # If null, it's global. If 'management', it's for all management offices.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    responses = relationship("QuestionResponse", back_populates="question")


class QuestionResponse(Base):
    __tablename__ = "question_responses"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(Integer, ForeignKey("feedback.id"), index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True, index=True)
    answer = Column(String(255))
    # Stores the actual question label visible on the form at submission time.
    # This is the ground truth — it overrides any DB question lookup by ID.
    question_text = Column(String(500), nullable=True)

    feedback = relationship("Feedback", back_populates="responses")
    question = relationship("Question", back_populates="responses")


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    action = Column(String(100))  # e.g., 'read_message', 'reply_message'
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.now)
