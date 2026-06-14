from celery import Celery
from celery.schedules import crontab

from config import get_settings

settings = get_settings()

celery = Celery(
    "skripsi",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["tasks.insight", "tasks.memory"],
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Jakarta",
    enable_utc=False,
    task_routes={
        "tasks.insight.generate_insight_task": {"queue": "insight"},
        "tasks.memory.compress_memory_task": {"queue": "memory"},
        "tasks.memory.compress_all_users_task": {"queue": "memory"},
    },
    beat_schedule={
        # Compress memory tiap awal bulan jam 02:00 WIB
        "compress-memory-monthly": {
            "task": "tasks.memory.compress_all_users_task",
            "schedule": crontab(minute=0, hour=2, day_of_month=1),
        },
    },
)


def generate_insight_task(*args, **kwargs):  # re-export utk import gampang
    from tasks.insight import generate_insight_task as _t
    return _t


def compress_memory_task(*args, **kwargs):
    from tasks.memory import compress_memory_task as _t
    return _t


# Lazy proxies supaya endpoint bisa langsung pakai .delay()
from tasks.insight import generate_insight_task  # noqa: E402,F401
from tasks.memory import compress_memory_task  # noqa: E402,F401
