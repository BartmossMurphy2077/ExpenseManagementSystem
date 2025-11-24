import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from . import models
from .config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class AuthService:
    """
    Authentication and token utilities.
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token. Expects `data` to contain a 'sub' key (user id)
        or include it here before calling.
        """
        to_encode = data.copy()
        now = datetime.utcnow()
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=settings.access_token_expire_minutes)

        # Standard claims
        to_encode.update({"exp": expire, "iat": now})
        # Keep token payload small: include `sub` (user id) and optionally other minimal claims
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """
        Verify token and return subject (user id) or None if invalid/expired.
        """
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: Optional[str] = payload.get("sub")
            return user_id
        except ExpiredSignatureError:
            logger.info("JWT token expired")
            return None
        except JWTError as e:
            logger.warning("JWT verification failed: %s", e)
            return None

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_authenticated_user(db: Session, token: str) -> models.User:
        """
        Higher level helper that decodes token, fetches user and raises HTTPException
        on failure. Use in FastAPI dependencies.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        user_id = AuthService.verify_token(token)
        if user_id is None:
            raise credentials_exception

        user = AuthService.get_user_by_id(db, user_id)
        if user is None:
            raise credentials_exception

        return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(lambda: None),
) -> models.User:
    """
    FastAPI dependency that returns the authenticated user.
    Accepts an injected `db` dependency for testing. If `db` is None it will
    import and use the real get_db generator (like in production).
    """
    # Import here to avoid circular import at module import time
    from .database import get_db

    # If no db provided by DI, obtain one from generator
    if db is None:
        db_session = next(get_db())
        close_session = True
    else:
        db_session = db
        close_session = False

    try:
        return AuthService.get_authenticated_user(db_session, credentials.credentials)
    finally:
        if close_session:
            db_session.close()


# Backward compatibility wrappers (keeps older imports working)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return AuthService.verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return AuthService.get_password_hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return AuthService.create_access_token(data, expires_delta)


# Constants for backward compatibility
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
