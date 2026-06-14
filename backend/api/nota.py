import io
import json
import re
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from config import get_settings
from database import get_db
from deepseek_client import chat as deepseek_chat
from models import Nota, TrainingData, User
from schemas.nota import NotaAnalyzeOut, NotaItem
from security import get_current_user

router = APIRouter(prefix="/nota", tags=["nota"])

settings = get_settings()

_paddle_ocr = None


def _get_ocr():
    global _paddle_ocr
    if _paddle_ocr is None:
        try:
            from paddleocr import PaddleOCR
            _paddle_ocr = PaddleOCR(use_angle_cls=True, lang="id", show_log=False)
        except Exception as e:
            print(f"[nota] PaddleOCR init gagal: {e}")
            _paddle_ocr = False
    return _paddle_ocr or None


def _ocr_image(image_path: str) -> str:
    ocr = _get_ocr()
    if not ocr:
        return ""
    try:
        result = ocr.ocr(image_path, cls=True)
        if result and result[0]:
            return "\n".join(line[1][0] for line in result[0] if line)
    except Exception as e:
        print(f"[nota] OCR error: {e}")
    return ""


def _retrieve_rag(db: Session, ocr_text: str, k: int = 5) -> str:
    rows = (
        db.query(TrainingData.teks_input)
        .filter(TrainingData.verified.is_(True))
        .all()
    )
    docs = [r[0] for r in rows if r[0]]
    if not docs:
        return ""

    tokens = {w for w in re.findall(r"\w+", ocr_text.lower()) if len(w) > 4}

    def score(doc: str) -> int:
        doc_tokens = {w for w in re.findall(r"\w+", doc.lower()) if len(w) > 4}
        return len(tokens & doc_tokens)

    ranked = sorted(docs, key=score, reverse=True)
    top = [d for d in ranked if score(d) > 0][:k] or ranked[:k]
    return " | ".join(top)


def _try_parse_json(text: str) -> dict | None:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def _build_prompt(ocr_text: str, rag_context: str) -> str:
    return f"""Anda asisten parsing nota transaksi Indonesia.

===== TEKS OCR (PaddleOCR) =====
{ocr_text}

===== KONTEKS RAG =====
{rag_context}

Tugas:
1. Tentukan apakah teks di atas memang struk/nota.
2. Klasifikasi kategori (Makanan/Transportasi/Belanja/Hiburan/Kesehatan/Tagihan/Lainnya).
3. Ekstrak merchant, daftar item, dan total.

Balas HANYA JSON valid (tanpa markdown) dengan struktur:
{{
  "status_validasi": "Sesuai" | "Tidak Sesuai",
  "kategori": "...",
  "merchant": "...",
  "items": [{{"nama_item": "...", "qty": 1, "harga_satuan": 0}}],
  "total": 0
}}
"""


@router.post("/analyze", response_model=NotaAnalyzeOut)
async def analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(415, detail="File harus berupa gambar")

    raw = await file.read()
    if len(raw) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, detail=f"Ukuran maksimal {settings.max_upload_mb} MB")

    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    ext = (Path(file.filename or "nota.jpg").suffix or ".jpg").lower()
    saved_path = Path(settings.upload_dir) / f"{uuid4()}{ext}"

    try:
        Image.open(io.BytesIO(raw)).convert("RGB").save(saved_path)
    except Exception as e:
        raise HTTPException(400, detail=f"Gambar tidak valid: {e}")

    ocr_text = _ocr_image(str(saved_path))
    rag_context = _retrieve_rag(db, ocr_text)

    try:
        raw_resp = deepseek_chat(_build_prompt(ocr_text, rag_context), temperature=0.2)
    except Exception as e:
        raise HTTPException(502, detail=f"DeepSeek gagal: {e}")

    parsed = _try_parse_json(raw_resp) or {
        "status_validasi": "Tidak Sesuai",
        "kategori": None,
        "merchant": None,
        "items": [],
        "total": 0,
    }

    ocr_status = parsed.get("status_validasi") or ("Sesuai" if ocr_text else "Tidak Sesuai")

    nota = Nota(
        user_id=user.id,
        path_foto=str(saved_path),
        ocr_raw_text=ocr_text or None,
        ocr_status=ocr_status,
    )
    db.add(nota)
    db.commit()
    db.refresh(nota)

    items = [
        NotaItem(
            nama_item=str(it.get("nama_item") or it.get("nama") or ""),
            qty=int(it.get("qty") or it.get("jumlah") or 1),
            harga_satuan=Decimal(str(it.get("harga_satuan") or it.get("harga") or 0)),
        )
        for it in (parsed.get("items") or [])
    ]

    return NotaAnalyzeOut(
        nota_id=nota.id,
        ocr_status=ocr_status,
        merchant=parsed.get("merchant"),
        kategori=parsed.get("kategori"),
        total=Decimal(str(parsed.get("total") or 0)),
        items=items,
        ocr_text=ocr_text,
        raw=parsed,
    )
