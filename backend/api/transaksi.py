from datetime import date as ddate
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session, selectinload

from database import get_db
from models import ItemTransaksi, Kategori, Transaksi, User
from schemas.transaksi import (
    ItemOut, TransaksiIn, TransaksiListOut, TransaksiOut,
)
from security import get_current_user

router = APIRouter(prefix="/transaksi", tags=["transaksi"])


def _to_out(trx: Transaksi, tipe: Optional[str] = None) -> TransaksiOut:
    return TransaksiOut(
        id=trx.id,
        kategori_id=trx.kategori_id,
        nominal=trx.nominal,
        kategori=trx.kategori,
        merchant=trx.merchant,
        tanggal_transaksi=trx.tanggal_transaksi,
        deskripsi=trx.deskripsi,
        metode_bayar=trx.metode_bayar,
        nota_id=trx.nota_id,
        created_at=trx.created_at,
        items=[ItemOut.model_validate(it) for it in trx.items],
        tipe=tipe if tipe is not None else (trx.kategori_obj.tipe if trx.kategori_obj else None),
    )


def _compute_nominal(payload: TransaksiIn) -> Decimal:
    if payload.items:
        return sum(
            (Decimal(it.harga_satuan) * it.qty for it in payload.items),
            Decimal("0"),
        )
    return Decimal(payload.nominal)


@router.get("", response_model=TransaksiListOut)
def list_transaksi(
    limit: int = Query(default=20, ge=1, le=100),
    cursor: Optional[str] = None,
    tipe: Optional[str] = None,
    tanggal_dari: Optional[ddate] = None,
    tanggal_sampai: Optional[ddate] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = (
        db.query(Transaksi)
        .options(selectinload(Transaksi.items), selectinload(Transaksi.kategori_obj))
        .filter(Transaksi.user_id == user.id)
    )
    if tipe in {"pemasukan", "pengeluaran"}:
        q = q.join(Kategori, Transaksi.kategori_id == Kategori.id).filter(Kategori.tipe == tipe)
    if tanggal_dari:
        q = q.filter(Transaksi.tanggal_transaksi >= tanggal_dari)
    if tanggal_sampai:
        q = q.filter(Transaksi.tanggal_transaksi <= tanggal_sampai)

    total = q.count()
    q = q.order_by(desc(Transaksi.tanggal_transaksi), desc(Transaksi.created_at))

    try:
        offset = int(cursor) if cursor else 0
    except ValueError:
        offset = 0

    rows = q.offset(offset).limit(limit).all()
    next_cursor = str(offset + limit) if offset + limit < total else None

    return TransaksiListOut(
        items=[_to_out(r) for r in rows],
        total=total,
        next_cursor=next_cursor,
    )


@router.post("", response_model=TransaksiOut, status_code=201)
def create_transaksi(
    payload: TransaksiIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    kategori = db.query(Kategori).filter(Kategori.id == payload.kategori_id).first()
    if not kategori:
        raise HTTPException(422, detail="Kategori tidak ditemukan")

    trx = Transaksi(
        user_id=user.id,
        kategori_id=payload.kategori_id,
        nominal=_compute_nominal(payload),
        kategori=payload.kategori or kategori.nama,
        merchant=payload.merchant,
        tanggal_transaksi=payload.tanggal_transaksi,
        deskripsi=payload.deskripsi,
        metode_bayar=payload.metode_bayar,
        nota_id=payload.nota_id,
    )
    db.add(trx)
    db.flush()

    for it in payload.items:
        db.add(ItemTransaksi(
            transaksi_id=trx.id,
            nama_item=it.nama_item,
            qty=it.qty,
            harga_satuan=it.harga_satuan,
            kategori=it.kategori,
        ))

    db.commit()
    db.refresh(trx)
    return _to_out(trx, tipe=kategori.tipe)


@router.get("/{trx_id}", response_model=TransaksiOut)
def get_transaksi(
    trx_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    trx = (
        db.query(Transaksi)
        .options(selectinload(Transaksi.items), selectinload(Transaksi.kategori_obj))
        .filter(Transaksi.id == trx_id, Transaksi.user_id == user.id)
        .first()
    )
    if not trx:
        raise HTTPException(404, detail="Transaksi tidak ditemukan")
    return _to_out(trx)


@router.put("/{trx_id}", response_model=TransaksiOut)
def update_transaksi(
    trx_id: int,
    payload: TransaksiIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    trx = (
        db.query(Transaksi)
        .filter(Transaksi.id == trx_id, Transaksi.user_id == user.id)
        .first()
    )
    if not trx:
        raise HTTPException(404, detail="Transaksi tidak ditemukan")

    kategori = db.query(Kategori).filter(Kategori.id == payload.kategori_id).first()
    if not kategori:
        raise HTTPException(422, detail="Kategori tidak ditemukan")

    trx.kategori_id = payload.kategori_id
    trx.kategori = payload.kategori or kategori.nama
    trx.merchant = payload.merchant
    trx.tanggal_transaksi = payload.tanggal_transaksi
    trx.deskripsi = payload.deskripsi
    trx.metode_bayar = payload.metode_bayar
    trx.nota_id = payload.nota_id
    trx.nominal = _compute_nominal(payload)

    db.query(ItemTransaksi).filter(ItemTransaksi.transaksi_id == trx.id).delete()
    for it in payload.items:
        db.add(ItemTransaksi(
            transaksi_id=trx.id,
            nama_item=it.nama_item,
            qty=it.qty,
            harga_satuan=it.harga_satuan,
            kategori=it.kategori,
        ))

    db.commit()
    db.refresh(trx)
    return _to_out(trx, tipe=kategori.tipe)


@router.delete("/{trx_id}", status_code=204)
def delete_transaksi(
    trx_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    trx = (
        db.query(Transaksi)
        .filter(Transaksi.id == trx_id, Transaksi.user_id == user.id)
        .first()
    )
    if not trx:
        raise HTTPException(404, detail="Transaksi tidak ditemukan")
    db.delete(trx)
    db.commit()
