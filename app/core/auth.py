import secrets
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.database import get_db
from config import settings


def generate_cookie_token() -> str:
    """Generate a secure random token for user session"""
    return secrets.token_urlsafe(32)


def get_or_create_user_by_cookie(db: Session, cookie_token: str) -> User:
    """Get user by cookie token or create new user if token doesn't exist"""
    user = db.query(User).filter(User.cookie_token == cookie_token).first()
    
    if not user:
        # Create new user with the provided cookie token
        user = User(cookie_token=cookie_token)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


def get_user_from_request(request: Request, db: Session) -> User:
    """Extract user from request cookie or create new user"""
    cookie_token = request.cookies.get(settings.cookie_name)
    
    if not cookie_token:
        # Generate new cookie token
        cookie_token = generate_cookie_token()
    
    return get_or_create_user_by_cookie(db, cookie_token)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Dependency to get current user from request"""
    return get_user_from_request(request, db)


def verify_task_ownership(db: Session, task_id: int, user_id: int) -> bool:
    """Verify that the task belongs to the user"""
    from app.models.task import Task
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    return task is not None
