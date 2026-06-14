# Skripsi — FinanceAI

Aplikasi keuangan personal full-stack berbasis **SvelteKit + FastAPI + PostgreSQL + DeepSeek**.
Backend dideploy via **Dokploy** (`financego.cloud`); pengembangan lokal pakai Docker Compose.

```
┌────────────────────────────────────────────────────────────┐
│ Nginx (443/80) — TLS, reverse proxy                        │
│   ├── /          → frontend (SvelteKit dev / static build) │
│   ├── /api/*     → backend  (FastAPI :8000)                │
│   └── /api/insight/stream → SSE (no-buffer)                │
├────────────────────────────────────────────────────────────┤
│ frontend  (SvelteKit + Tailwind + Capacitor)               │
│ backend   (FastAPI + SQLAlchemy + Alembic + Celery)        │
│ postgres  (16-alpine)                                      │
│ redis     (broker Celery)                                  │
│ DeepSeek API (parsing nota, AI Insight, AI Memory)         │
└────────────────────────────────────────────────────────────┘
```

## Struktur

```
skripsi/
├── docker-compose.yml
├── Makefile
├── nginx/
├── backend/                     # FastAPI
│   ├── main.py, config.py, database.py, models.py, security.py
│   ├── deepseek_client.py       # DeepSeek API wrapper
│   ├── api/                     # routers fase 1-7
│   ├── schemas/                 # pydantic
│   ├── alembic/                 # migrasi
│   ├── celery_app.py, tasks/    # async insight & memory
│   └── tests/
└── frontend/                    # SvelteKit
    └── src/
        ├── lib/                 # api, stores, auth, components
        └── routes/              # /login /register /home /manual /scan /budget /statistik /insight /profil
```

## Setup lokal

```bash
cp backend/.env.example backend/.env       # isi DATABASE_URL, JWT_SECRET, DEEPSEEK_API_KEY
cp frontend/.env.example frontend/.env     # arahkan ke API base
```

Penting:
- `DEEPSEEK_API_KEY` wajib (dipakai untuk parsing nota, insight, memory).
- `DATABASE_URL` arahkan ke Postgres (lokal compose atau Dokploy).
- `JWT_SECRET` rotate sebelum publish.

## Jalankan

```bash
make up                      # build + start semua
make migrate                 # alembic upgrade head (sudah seed kategori + RAG corpus)
```

Setelah sehat, buka:
- Frontend: <https://localhost>
- API docs: <https://localhost/api/docs>
- Health: <https://localhost/healthz>

## Build APK (Capacitor)

```bash
cd frontend
npm run build
npx cap add android        # sekali saja
npx cap sync
npx cap open android       # buka Android Studio, build APK
```

## Testing

```bash
make test
```

## Fase

| Fase | Fitur                       | Lokasi utama |
| ---- | --------------------------- | ------------ |
| 1    | Setup & Auth (JWT)          | `backend/api/auth.py`, `frontend/src/routes/{login,register}` |
| 2    | Frontend mobile-first       | `frontend/src/lib/components/MobileShell.svelte` |
| 3    | Transaksi manual + items    | `backend/api/transaksi.py`, `frontend/src/routes/manual` |
| 4    | Scan nota (PaddleOCR + DeepSeek + RAG dari `training_data`) | `backend/api/nota.py`, `frontend/src/routes/scan` |
| 5    | Budget & statistik          | `backend/api/budget.py`, `frontend/src/routes/{budget,statistik}` |
| 6    | AI Insight (DeepSeek async) | `backend/api/insight.py`, `tasks/insight.py` |
| 7    | AI Memory (Celery beat)     | `backend/api/memory.py`, `tasks/memory.py` |
| 8    | Polish & deploy             | profil, push (Capacitor), Docker, Nginx, Dokploy |
