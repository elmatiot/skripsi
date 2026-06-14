from decimal import Decimal
from typing import Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotaItem(BaseModel):
    nama_item: str
    qty: int = 1
    harga_satuan: Decimal = Decimal("0")


class NotaAnalyzeOut(BaseModel):
    nota_id: int
    ocr_status: Optional[str] = None
    merchant: Optional[str] = None
    kategori: Optional[str] = None
    total: Decimal = Decimal("0")
    items: List[NotaItem] = []
    ocr_text: Optional[str] = None
    raw: Optional[Any] = None


class NotaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    path_foto: Optional[str] = None
    ocr_status: Optional[str] = None
    tanggal_scan: datetime
