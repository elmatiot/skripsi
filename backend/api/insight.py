import asyncio
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from database import get_db
from models import AIInsight, User
from schemas.insight import InsightOut, InsightTriggerOut
from security import get_current_user

router = APIRouter(prefix="/insight", tags=["insight"])


@router.get("", response_model=List[InsightOut])
def list_insight(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = (
        db.query(AIInsight)
        .filter(AIInsight.user_id == user.id)
        .order_by(AIInsight.created_at.desc())
        .limit(50)
        .all()
    )
    return [InsightOut.model_validate(r) for r in rows]


@router.post("/generate", response_model=InsightTriggerOut, status_code=202)
def trigger_generate(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from celery_app import generate_insight_task
    task = generate_insight_task.delay(str(user.id))
    return InsightTriggerOut(task_id=task.id)


@router.post("/{insight_id}/read", response_model=InsightOut)
def mark_read(
    insight_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = (
        db.query(AIInsight)
        .filter(AIInsight.id == insight_id, AIInsight.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(404)
    row.sudah_dibaca = True
    db.commit()
    db.refresh(row)
    return InsightOut.model_validate(row)


@router.get("/stream")
async def stream_insight(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    last_seen_id: set[int] = set()

    async def event_gen():
        nonlocal last_seen_id
        while True:
            unread = (
                db.query(AIInsight)
                .filter(AIInsight.user_id == user.id, AIInsight.sudah_dibaca == False)  # noqa: E712
                .order_by(AIInsight.created_at.desc())
                .limit(5)
                .all()
            )
            new = [r for r in unread if r.id not in last_seen_id]
            for r in new:
                last_seen_id.add(r.id)
                yield {
                    "event": "insight",
                    "data": json.dumps({
                        "id": r.id,
                        "judul": r.judul,
                        "konten": r.konten,
                        "tipe": r.tipe,
                        "created_at": r.created_at.isoformat(),
                    }),
                }
            yield {"event": "ping", "data": "1"}
            await asyncio.sleep(5)

    return EventSourceResponse(event_gen())
