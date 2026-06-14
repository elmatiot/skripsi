from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BudgetIn(BaseModel):
    kategori_id: int
    nominal_budget: Decimal = Field(ge=0)
    tahun: int = Field(ge=2000, le=2100)
    bulan: int = Field(ge=1, le=12)


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    kategori_id: int
    nominal_budget: Decimal
    tahun: int
    bulan: int


class BudgetStatus(BaseModel):
    kategori_id: int
    kategori_nama: str
    kategori_warna: Optional[str] = None
    nominal_budget: Decimal
    terpakai: Decimal
    sisa: Decimal
    persen: float


class CategoryBreakdown(BaseModel):
    kategori_id: int
    kategori_nama: str
    warna_hex: Optional[str] = None
    total: Decimal


class StatistikSummary(BaseModel):
    tahun: int
    bulan: int
    total_pemasukan: Decimal
    total_pengeluaran: Decimal
    saldo: Decimal
    breakdown_pengeluaran: List[CategoryBreakdown]
    breakdown_pemasukan: List[CategoryBreakdown]
