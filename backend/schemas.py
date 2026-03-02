from datetime import datetime
from pydantic import BaseModel
from typing import Literal, Optional

# User Registration
class UserCreate(BaseModel):
    fullname: str
    username: Optional[str] = None
    email: Optional[str] = None
    password: str
    role: Literal['student', 'staff', 'visitor', 'admin']
    department_id: Optional[int] = None


class UserOut(BaseModel):
    id: int
    fullname: str
    email: str
    role: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Enhanced JWT Token schema with user info
class Token(BaseModel):
    access_token: str
    token_type: str
    role: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    fullname: Optional[str] = None
    department_id: Optional[int] = None


# Login Request
class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str


# Forgot & Reset Password
class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# Feedback Submission
class FeedbackCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    category: str
    office: str
    message: str
    anonymous: str  # 'true' or 'false'
    department_id: Optional[int] = None
    rating: Optional[str] = None
    q_0: Optional[str] = None
    q_1: Optional[str] = None
    q_2: Optional[str] = None
    q_3: Optional[str] = None
    q_4: Optional[str] = None


class FeedbackOut(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[str]
    category: str
    office: str
    message: str
    anonymous: str
    department_id: Optional[int]
    created_at: datetime
    rating: Optional[str] = None
    
    # Status fields
    is_read: Optional[bool] = False
    read_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    reply_message: Optional[str] = None
    tracking_id: Optional[str] = None
    q_0: Optional[str] = None
    q_1: Optional[str] = None
    q_2: Optional[str] = None
    q_3: Optional[str] = None
    q_4: Optional[str] = None

    class Config:
        from_attributes = True


# Optional: Add a schema for marking feedback as read
class FeedbackReadUpdate(BaseModel):
    is_read: bool = True
    read_at: datetime = datetime.now()


# Optional: Add a schema for replying to feedback
class FeedbackReplyCreate(BaseModel):
    feedback_id: int
    email: str
    subject: str
    message: str


# Optional: Add a schema for feedback statistics (for admin dashboard)
class FeedbackStats(BaseModel):
    total: int
    unread: int
    read: int
    replied: int
    today: int

# Anonymous feedback tracking
class FeedbackTrackRequest(BaseModel):
    email: Optional[str] = None
    tracking_id: Optional[str] = None