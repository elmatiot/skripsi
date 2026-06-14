from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class KategoriOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nama: str
    tipe: Optional[str] = None
    icon: Optional[str] = None
    warna_hex: Optional[str] = None


class KategoriIn(BaseModel):
    nama: str = Field(min_length=1, max_length=255)
    tipe: Optional[str] = Field(default=None)
    warna_hex: Optional[str] = Field(default=None, max_length=7)
    icon: Optional[str] = Field(default=None, max_length=255)


class MessageOut(BaseModel):
    message: str
    detail: Optional[str] = None
