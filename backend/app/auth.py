# backend/app/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from . import models
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("sub")
            return user_id
        except JWTError:
            return None

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == user_id).first()


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(lambda: None)
) -> models.User:
    # Import here to avoid circular import
    from .database import get_db

    # Get database session - this will use the overridden dependency in tests
    if db is None:
        db_session = next(get_db())
        close_session = True
    else:
        db_session = db
        close_session = False

    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        user_id = AuthService.verify_token(credentials.credentials)
        if user_id is None:
            raise credentials_exception

        user = AuthService.get_user_by_id(db_session, user_id)
        if user is None:
            raise credentials_exception

        return user
    finally:
        if close_session:
            db_session.close()


# Backward compatibility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return AuthService.verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return AuthService.get_password_hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return AuthService.create_access_token(data, expires_delta)


# Constants for backward compatibility
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
