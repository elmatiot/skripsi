from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class InsightOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    judul: str
    konten: str
    tipe: str
    sudah_dibaca: bool
    created_at: datetime


class InsightTriggerOut(BaseModel):
    task_id: str
    message: str = "Insight sedang dibuat di background"


class MemoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    topik: str
    ringkasan: str
    fakta: Optional[Any] = None
    versi: int
    updated_at: datetime
