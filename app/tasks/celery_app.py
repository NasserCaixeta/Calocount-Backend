from celery import Celery

from app.config import settings

celery_app = Celery(
    "calocount",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.ai_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_always_eager=settings.APP_ENV == "development",
    task_eager_propagates=True,
)
