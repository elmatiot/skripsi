from fastapi import APIRouter

from .auth import router as auth_router
from .kategori import router as kategori_router
from .transaksi import router as transaksi_router
from .nota import router as nota_router
from .budget import router as budget_router
from .insight import router as insight_router
from .memory import router as memory_router
from .profile import router as profile_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(kategori_router)
api_router.include_router(transaksi_router)
api_router.include_router(nota_router)
api_router.include_router(budget_router)
api_router.include_router(insight_router)
api_router.include_router(memory_router)
api_router.include_router(profile_router)
