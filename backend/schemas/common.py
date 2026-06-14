from typing import Optional
from pydantic import BaseModel, ConfigDict


class KategoriOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nama: str
    tipe: Optional[str] = None
    icon: Optional[str] = None
    warna_hex: Optional[str] = None


class MessageOut(BaseModel):
    message: str
    detail: Optional[str] = None
