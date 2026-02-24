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
    created_at = Column(DateTime, default=datetime.utcnow)

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
    created_at = Column(DateTime, default=datetime.utcnow)
    rating = Column(String(10), nullable=True)
    
    # Status fields
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    reply_message = Column(Text, nullable=True)

    department = relationship("Department", back_populates="feedbacks")


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    action = Column(String(100))  # e.g., 'read_message', 'reply_message'
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
