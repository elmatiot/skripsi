from datetime import date as ddate
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Budget, Kategori, Transaksi, User
from schemas.budget import (
    BudgetIn, BudgetOut, BudgetStatus, CategoryBreakdown, StatistikSummary,
)
from security import get_current_user

router = APIRouter(prefix="/budget", tags=["budget"])


def _periode_to_dates(tahun: int, bulan: int) -> tuple[ddate, ddate]:
    start = ddate(tahun, bulan, 1)
    if bulan == 12:
        end = ddate(tahun + 1, 1, 1)
    else:
        end = ddate(tahun, bulan + 1, 1)
    return start, end


@router.get("", response_model=List[BudgetOut])
def list_budget(
    tahun: Optional[int] = Query(default=None, ge=2000, le=2100),
    bulan: Optional[int] = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Budget).filter(Budget.user_id == user.id)
    if tahun is not None:
        q = q.filter(Budget.tahun == tahun)
    if bulan is not None:
        q = q.filter(Budget.bulan == bulan)
    return [
        BudgetOut.model_validate(b)
        for b in q.order_by(Budget.tahun.desc(), Budget.bulan.desc(), Budget.kategori_id).all()
    ]


@router.post("", response_model=BudgetOut, status_code=201)
def upsert_budget(
    payload: BudgetIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    b = (
        db.query(Budget)
        .filter(
            Budget.user_id == user.id,
            Budget.kategori_id == payload.kategori_id,
            Budget.tahun == payload.tahun,
            Budget.bulan == payload.bulan,
        )
        .first()
    )
    if b:
        b.nominal_budget = payload.nominal_budget
    else:
        b = Budget(
            user_id=user.id,
            kategori_id=payload.kategori_id,
            nominal_budget=payload.nominal_budget,
            tahun=payload.tahun,
            bulan=payload.bulan,
        )
        db.add(b)
    db.commit()
    db.refresh(b)
    return BudgetOut.model_validate(b)


@router.delete("/{budget_id}", status_code=204)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    b = (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == user.id)
        .first()
    )
    if not b:
        raise HTTPException(404)
    db.delete(b)
    db.commit()


@router.get("/status", response_model=List[BudgetStatus])
def budget_status(
    tahun: int = Query(ge=2000, le=2100),
    bulan: int = Query(ge=1, le=12),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    start, end = _periode_to_dates(tahun, bulan)

    spent_rows = dict(
        db.query(Transaksi.kategori_id, func.coalesce(func.sum(Transaksi.nominal), 0))
        .join(Kategori, Transaksi.kategori_id == Kategori.id)
        .filter(
            Transaksi.user_id == user.id,
            Kategori.tipe == "pengeluaran",
            Transaksi.tanggal_transaksi >= start,
            Transaksi.tanggal_transaksi < end,
        )
        .group_by(Transaksi.kategori_id)
        .all()
    )

    budgets = (
        db.query(Budget, Kategori)
        .join(Kategori, Budget.kategori_id == Kategori.id)
        .filter(Budget.user_id == user.id, Budget.tahun == tahun, Budget.bulan == bulan)
        .all()
    )

    out: List[BudgetStatus] = []
    for b, k in budgets:
        terpakai = Decimal(str(spent_rows.get(b.kategori_id, 0)))
        sisa = Decimal(b.nominal_budget) - terpakai
        persen = float(terpakai / b.nominal_budget * 100) if b.nominal_budget else 0.0
        out.append(BudgetStatus(
            kategori_id=k.id,
            kategori_nama=k.nama,
            kategori_warna=k.warna_hex,
            nominal_budget=b.nominal_budget,
            terpakai=terpakai,
            sisa=sisa,
            persen=round(persen, 2),
        ))
    return out


@router.get("/statistik", response_model=StatistikSummary)
def statistik(
    tahun: int = Query(ge=2000, le=2100),
    bulan: int = Query(ge=1, le=12),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    start, end = _periode_to_dates(tahun, bulan)

    def _sum(tipe: str) -> Decimal:
        val = (
            db.query(func.coalesce(func.sum(Transaksi.nominal), 0))
            .join(Kategori, Transaksi.kategori_id == Kategori.id)
            .filter(
                Transaksi.user_id == user.id,
                Kategori.tipe == tipe,
                Transaksi.tanggal_transaksi >= start,
                Transaksi.tanggal_transaksi < end,
            )
            .scalar()
            or 0
        )
        return Decimal(str(val))

    income_total = _sum("pemasukan")
    expense_total = _sum("pengeluaran")

    def _breakdown(tipe: str) -> List[CategoryBreakdown]:
        rows = (
            db.query(
                Kategori.id, Kategori.nama, Kategori.warna_hex,
                func.coalesce(func.sum(Transaksi.nominal), 0),
            )
            .join(Transaksi, Transaksi.kategori_id == Kategori.id)
            .filter(
                Transaksi.user_id == user.id,
                Kategori.tipe == tipe,
                Transaksi.tanggal_transaksi >= start,
                Transaksi.tanggal_transaksi < end,
            )
            .group_by(Kategori.id, Kategori.nama, Kategori.warna_hex)
            .order_by(func.sum(Transaksi.nominal).desc())
            .all()
        )
        return [
            CategoryBreakdown(
                kategori_id=r[0], kategori_nama=r[1], warna_hex=r[2], total=Decimal(str(r[3]))
            )
            for r in rows
        ]

    return StatistikSummary(
        tahun=tahun,
        bulan=bulan,
        total_pemasukan=income_total,
        total_pengeluaran=expense_total,
        saldo=income_total - expense_total,
        breakdown_pengeluaran=_breakdown("pengeluaran"),
        breakdown_pemasukan=_breakdown("pemasukan"),
    )
