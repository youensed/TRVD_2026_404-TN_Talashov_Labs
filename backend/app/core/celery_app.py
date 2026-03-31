from __future__ import annotations

from celery import Celery

from app.core.config import get_settings


settings = get_settings()

celery_app = Celery(
    "pmc_crm",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    timezone="Europe/Kyiv",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    beat_schedule={
        "generate-appointment-reminders": {
            "task": "app.modules.reminders.tasks.generate_appointment_reminders",
            "schedule": 1800.0,
        },
    },
)

celery_app.autodiscover_tasks(["app.modules.reminders"])

