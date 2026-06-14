import traceback
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas.auth import LoginIn, RegisterIn, TokenOut, UserOut
from security import create_access_token, hash_password, verify_password, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    try:
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(409, detail="Email sudah terdaftar")
        user = User(
            email=payload.email,
            nama=payload.nama,
            password_hash=hash_password(payload.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token(str(user.id), extra={"email": user.email})
        return TokenOut(access_token=token, user=UserOut.model_validate(user))
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, detail=f"{type(e).__name__}: {e}")


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == payload.email).first()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(401, detail="Email atau password salah")
        token = create_access_token(str(user.id), extra={"email": user.email})
        return TokenOut(access_token=token, user=UserOut.model_validate(user))
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, detail=f"{type(e).__name__}: {e}")


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return UserOut.model_validate(current)
