from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import os

from models import User
from database import get_db
from config import Config

# =========================
# SECURITY CONFIG
# =========================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login", auto_error=False)

SECRET_KEY = Config.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

RESET_TOKEN_SECRET = os.getenv("RESET_TOKEN_SECRET", SECRET_KEY)
RESET_TOKEN_EXPIRE_MINUTES = 30


# =========================
# PASSWORD HELPERS
# =========================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    # bcrypt limitation
    if len(password) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password must not exceed 72 characters"
        )
    return pwd_context.hash(password)


# =========================
# AUTHENTICATION
# =========================

def authenticate_user(db: Session, email: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None, department_id: Optional[int] = None):
    query = db.query(User)
    if email:
        user = query.filter(User.email.ilike(email)).first()
    elif username:
        user = query.filter(User.username.ilike(username)).first()
    else:
        return False

    if not user:
        return False

    if not password or not verify_password(password, user.hashed_password):
        return False
    
    # If department_id is provided (admin login), verify it matches
    if department_id is not None and user.department_id != department_id:
        return False

    return user


# =========================
# JWT TOKEN HANDLING
# =========================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    access_token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Support token from query parameter (useful for CSV exports)
    token = token or access_token
    
    if not token:
        return None  # Allow anonymous access for some endpoints
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter((User.email == email) | (User.username == email)).first()
    if user is None:
        raise credentials_exception

    return user


# =========================
# PASSWORD RESET TOKENS
# =========================

def create_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": email,
        "exp": expire
    }
    return jwt.encode(payload, RESET_TOKEN_SECRET, algorithm=ALGORITHM)


def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, RESET_TOKEN_SECRET, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid reset token")
        return email
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")