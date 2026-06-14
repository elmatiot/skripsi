import logging
from datetime import date, timedelta

from celery import shared_task
from sqlalchemy import func

from database import SessionLocal
from deepseek_client import chat as deepseek_chat
from models import AIInsight, AIMemory, Kategori, Transaksi

log = logging.getLogger(__name__)


def _build_user_summary(db, user_id: int) -> dict:
    today = date.today()
    start = today.replace(day=1)
    last_30 = today - timedelta(days=30)

    income = db.query(func.coalesce(func.sum(Transaksi.nominal), 0)).join(
        Kategori, Transaksi.kategori_id == Kategori.id
    ).filter(
        Transaksi.user_id == user_id,
        Kategori.tipe == "pemasukan",
        Transaksi.tanggal_transaksi >= start,
    ).scalar() or 0

    expense = db.query(func.coalesce(func.sum(Transaksi.nominal), 0)).join(
        Kategori, Transaksi.kategori_id == Kategori.id
    ).filter(
        Transaksi.user_id == user_id,
        Kategori.tipe == "pengeluaran",
        Transaksi.tanggal_transaksi >= start,
    ).scalar() or 0

    breakdown = (
        db.query(Kategori.nama, func.coalesce(func.sum(Transaksi.nominal), 0))
        .join(Transaksi, Transaksi.kategori_id == Kategori.id)
        .filter(
            Transaksi.user_id == user_id,
            Kategori.tipe == "pengeluaran",
            Transaksi.tanggal_transaksi >= last_30,
        )
        .group_by(Kategori.nama)
        .order_by(func.sum(Transaksi.nominal).desc())
        .limit(5)
        .all()
    )

    return {
        "periode_bulan": start.strftime("%Y-%m"),
        "income_bulan": float(income),
        "expense_bulan": float(expense),
        "top_kategori_30hari": [{"nama": n, "total": float(t)} for n, t in breakdown],
    }


def _fetch_memory(db, user_id: int) -> str:
    rows = db.query(AIMemory).filter(AIMemory.user_id == user_id).all()
    if not rows:
        return "Belum ada memory user."
    return "\n".join(f"- [{r.topik}] {r.ringkasan}" for r in rows)


@shared_task(name="tasks.insight.generate_insight_task", queue="insight")
def generate_insight_task(user_id: str) -> str:
    db = SessionLocal()
    try:
        uid = int(user_id)
        summary = _build_user_summary(db, uid)
        memory = _fetch_memory(db, uid)

        prompt = f"""Anda adalah financial coach pribadi pengguna Indonesia.
Berdasarkan ringkasan & memory di bawah, hasilkan SATU insight (judul + isi)
yang spesifik, actionable, max 3 kalimat. Jawab dalam JSON murni:
{{"judul":"...","konten":"...","tipe":"saving|spending|warning|tips"}}

--- MEMORY USER ---
{memory}

--- RINGKASAN BULAN INI ---
{summary}
"""

        judul = "Insight Keuangan"
        konten = ""
        tipe = "general"

        try:
            raw = deepseek_chat(prompt)
            import json, re
            m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            parsed = {}
            if m:
                try:
                    parsed = json.loads(m.group(0))
                except Exception:
                    parsed = {}
            judul = parsed.get("judul") or "Insight Keuangan"
            konten = parsed.get("konten") or (raw or "")[:500]
            tipe = parsed.get("tipe") or "general"
        except Exception as e:
            log.exception("DeepSeek call gagal")
            judul = "Insight gagal dibuat"
            konten = f"Tidak bisa menghubungi AI: {e}. Coba lagi nanti atau cek konfigurasi DEEPSEEK_API_KEY."
            tipe = "warning"

        ins = AIInsight(
            user_id=uid,
            judul=(judul or "Insight Keuangan")[:160],
            konten=konten or "(kosong)",
            tipe=(tipe or "general")[:40],
        )
        db.add(ins)
        db.commit()
        db.refresh(ins)
        return str(ins.id)
    finally:
        db.close()
