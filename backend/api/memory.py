from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import AIMemory, User
from schemas.insight import MemoryOut
from security import get_current_user

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=List[MemoryOut])
def list_memory(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = (
        db.query(AIMemory)
        .filter(AIMemory.user_id == user.id)
        .order_by(AIMemory.updated_at.desc())
        .all()
    )
    return [MemoryOut.model_validate(r) for r in rows]


@router.post("/compress", status_code=202)
def trigger_compress(
    user: User = Depends(get_current_user),
):
    from celery_app import compress_memory_task
    task = compress_memory_task.delay(str(user.id))
    return {"task_id": task.id, "message": "Kompresi memory dijadwalkan"}
