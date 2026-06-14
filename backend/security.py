from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import get_settings
from database import get_db
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

settings = get_settings()


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain.encode()[:72])


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain.encode()[:72], hashed)


def create_access_token(sub: str, extra: Optional[dict] = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    cred_err = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau kedaluwarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise cred_err
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except Exception:
        raise cred_err

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise cred_err

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise cred_err
    return user
