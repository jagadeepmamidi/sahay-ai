"""
Authentication Module
=====================

JWT-based authentication for admin routes.
Uses the jwt_secret_key from config.

Author: Jagadeep Mamidi
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    _validate_secret()
    
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    _validate_secret()
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    FastAPI dependency that requires a valid admin JWT token.
    Use as: Depends(require_admin) on admin routes.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    payload = verify_token(credentials.credentials)
    
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return payload


def _validate_secret():
    """Ensure the JWT secret has been changed from default."""
    if settings.jwt_secret_key == "change-me-in-production":
        if settings.environment == "production":
            raise ValueError(
                "JWT_SECRET_KEY must be changed from default in production! "
                "Set a strong random secret in your .env file."
            )
        else:
            logger.warning(
                "Using default JWT secret. Change JWT_SECRET_KEY in .env for production."
            )


def generate_admin_token() -> str:
    """
    Generate an admin token for initial setup / testing.
    Call this from CLI: python -c "from app.core.auth import generate_admin_token; print(generate_admin_token())"
    """
    return create_access_token(
        data={"sub": "admin", "role": "admin"},
        expires_delta=timedelta(days=30)
    )
