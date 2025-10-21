"""
Authentication and authorization utilities
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# Simple token storage (in production, use JWT or proper session management)
# For MVP, we'll use a simple in-memory token store
_token_store = {}


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an access token for a user.
    In production, use JWT tokens with proper signing.
    """
    if expires_delta is None:
        expires_delta = timedelta(days=7)  # Default 7 day expiration

    token = secrets.token_urlsafe(32)
    expire = datetime.utcnow() + expires_delta

    _token_store[token] = {
        "user_id": user_id,
        "expires": expire
    }

    return token


def verify_token(token: str) -> Optional[int]:
    """
    Verify a token and return the user_id.
    Returns None if token is invalid or expired.
    """
    token_data = _token_store.get(token)

    if not token_data:
        return None

    if datetime.utcnow() > token_data["expires"]:
        # Token expired
        del _token_store[token]
        return None

    return token_data["user_id"]


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user.
    Used as a dependency in protected routes.
    """
    token = credentials.credentials

    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


def require_tier(required_tier: str):
    """
    Dependency to require a specific subscription tier.
    Usage: Depends(require_tier("pro"))
    """
    tier_hierarchy = {
        "free": 0,
        "pro": 1,
        "enterprise": 2
    }

    def check_tier(current_user: User = Depends(get_current_user)) -> User:
        user_tier_level = tier_hierarchy.get(current_user.tier, 0)
        required_tier_level = tier_hierarchy.get(required_tier, 0)

        if user_tier_level < required_tier_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {required_tier} tier subscription"
            )

        return current_user

    return check_tier
