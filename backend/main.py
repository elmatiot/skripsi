import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from api import api_router

settings = get_settings()
logging.getLogger("ppocr").setLevel(logging.WARNING)
log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Backend API skripsi: Auth, Transaksi, Nota OCR/VLM, Budget, AI Insight & Memory.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["meta"])
def root():
    return {
        "app": settings.app_name,
        "status": "running",
        "env": settings.app_env,
    }


@app.get("/healthz", tags=["meta"])
def healthz():
    return {"ok": True}
