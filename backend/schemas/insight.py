from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, field_validator


class InsightOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    judul: str
    konten: str
    tipe: str = "general"
    sudah_dibaca: bool = False
    created_at: datetime

    @field_validator("tipe", mode="before")
    @classmethod
    def _coerce_tipe(cls, v):
        return v or "general"

    @field_validator("sudah_dibaca", mode="before")
    @classmethod
    def _coerce_dibaca(cls, v):
        return bool(v) if v is not None else False

    @field_validator("judul", mode="before")
    @classmethod
    def _coerce_judul(cls, v):
        return v or "Insight"

    @field_validator("konten", mode="before")
    @classmethod
    def _coerce_konten(cls, v):
        return v or ""


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
