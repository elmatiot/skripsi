from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ItemIn(BaseModel):
    nama_item: str = Field(min_length=1, max_length=255)
    qty: int = Field(default=1, ge=1)
    harga_satuan: Decimal = Field(default=Decimal("0"), ge=0)
    kategori: Optional[str] = None


class ItemOut(ItemIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TransaksiIn(BaseModel):
    kategori_id: int
    nominal: Decimal = Field(ge=0)
    merchant: Optional[str] = Field(default=None, max_length=255)
    tanggal_transaksi: date
    deskripsi: Optional[str] = None
    metode_bayar: Optional[str] = Field(default=None, max_length=100)
    nota_id: Optional[int] = None
    items: List[ItemIn] = []


class TransaksiOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    kategori_id: int
    nominal: Decimal
    kategori: Optional[str] = None
    merchant: Optional[str] = None
    tanggal_transaksi: date
    deskripsi: Optional[str] = None
    metode_bayar: Optional[str] = None
    nota_id: Optional[int] = None
    created_at: datetime
    items: List[ItemOut] = []
    # Diambil dari kategori.tipe via join, untuk frontend yang masih perlu bedakan
    tipe: Optional[str] = None


class TransaksiListOut(BaseModel):
    items: List[TransaksiOut]
    total: int
    next_cursor: Optional[str] = None
