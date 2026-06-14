from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas.auth import UpdateProfileIn, UserOut
from security import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=UserOut)
def get_profile(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


@router.put("", response_model=UserOut)
def update_profile(
    payload: UpdateProfileIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.nama is not None:
        user.nama = payload.nama
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)
