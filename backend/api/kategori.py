from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Kategori
from schemas.common import KategoriOut
from security import get_current_user

router = APIRouter(prefix="/kategori", tags=["kategori"])


@router.get("", response_model=List[KategoriOut])
def list_kategori(
    tipe: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Kategori)
    if tipe in {"pemasukan", "pengeluaran"}:
        q = q.filter(Kategori.tipe == tipe)
    return [KategoriOut.model_validate(k) for k in q.order_by(Kategori.tipe, Kategori.id).all()]
