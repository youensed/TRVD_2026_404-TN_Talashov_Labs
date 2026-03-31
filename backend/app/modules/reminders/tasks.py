from __future__ import annotations

import asyncio

from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.db.session import SessionFactory
from app.modules.reminders.service import ReminderService


@celery_app.task(name="app.modules.reminders.tasks.generate_appointment_reminders")
def generate_appointment_reminders() -> int:
    settings = get_settings()
    return asyncio.run(_generate())


async def _generate() -> int:
    settings = get_settings()
    async with SessionFactory() as session:
        return await ReminderService(session).generate_due_reminders(
            hours_before=settings.reminder_horizon_hours,
            window_minutes=settings.reminder_window_minutes,
        )
