from datetime import date, timedelta

from celery import shared_task
from sqlalchemy import func

from database import SessionLocal
from deepseek_client import chat as deepseek_chat
from models import AIInsight, AIMemory, Kategori, Transaksi, User


def _user_fakta(db, user_id: int) -> dict:
    today = date.today()
    start = today - timedelta(days=30)

    expense = db.query(func.coalesce(func.sum(Transaksi.nominal), 0)).join(
        Kategori, Transaksi.kategori_id == Kategori.id
    ).filter(
        Transaksi.user_id == user_id,
        Kategori.tipe == "pengeluaran",
        Transaksi.tanggal_transaksi >= start,
    ).scalar() or 0

    top = (
        db.query(Kategori.nama, func.coalesce(func.sum(Transaksi.nominal), 0))
        .join(Transaksi, Transaksi.kategori_id == Kategori.id)
        .filter(
            Transaksi.user_id == user_id,
            Kategori.tipe == "pengeluaran",
            Transaksi.tanggal_transaksi >= start,
        )
        .group_by(Kategori.nama)
        .order_by(func.sum(Transaksi.nominal).desc())
        .limit(3)
        .all()
    )
    return {
        "total_pengeluaran_30hari": float(expense),
        "top_kategori": [{"nama": n, "total": float(t)} for n, t in top],
    }


def _last_insight_titles(db, user_id: int, n: int = 5) -> list[str]:
    rows = (
        db.query(AIInsight)
        .filter(AIInsight.user_id == user_id)
        .order_by(AIInsight.created_at.desc())
        .limit(n)
        .all()
    )
    return [r.judul for r in rows]


@shared_task(name="tasks.memory.compress_memory_task", queue="memory")
def compress_memory_task(user_id: str) -> str:
    db = SessionLocal()
    try:
        uid = int(user_id)
        fakta = _user_fakta(db, uid)
        insights = _last_insight_titles(db, uid)

        prompt = f"""Kompres profil keuangan pengguna jadi 2-3 kalimat ringkas (Bahasa Indonesia).
Topiknya: pola_pengeluaran. Output JSON murni:
{{"topik":"pola_pengeluaran","ringkasan":"..."}}

Fakta:
{fakta}

Insight terbaru:
{insights}
"""

        raw = deepseek_chat(prompt, temperature=0.2)

        import json, re
        m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        parsed = json.loads(m.group(0)) if m else {}

        topik = (parsed.get("topik") or "pola_pengeluaran")[:80]
        ringkasan = parsed.get("ringkasan") or raw[:500]

        mem = (
            db.query(AIMemory)
            .filter(AIMemory.user_id == uid, AIMemory.topik == topik)
            .first()
        )
        if mem:
            mem.ringkasan = ringkasan
            mem.fakta = fakta
            mem.versi += 1
        else:
            mem = AIMemory(
                user_id=uid, topik=topik, ringkasan=ringkasan, fakta=fakta, versi=1,
            )
            db.add(mem)
        db.commit()
        return topik
    finally:
        db.close()


@shared_task(name="tasks.memory.compress_all_users_task", queue="memory")
def compress_all_users_task() -> int:
    db = SessionLocal()
    try:
        ids = [str(uid) for (uid,) in db.query(User.id).all()]
    finally:
        db.close()
    for uid in ids:
        compress_memory_task.delay(uid)
    return len(ids)
