from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.appointments.repository import AppointmentRepository
from app.modules.audit.service import AuditService
from app.modules.common.enums import AuditEventType
from app.modules.common.utils import to_uuid
from app.modules.reminders.model import ReminderEvent
from app.modules.reminders.repository import ReminderRepository


@dataclass(slots=True)
class ReminderService:
    session: AsyncSession

    async def generate_due_reminders(self, *, hours_before: int, window_minutes: int) -> int:
        appointment_repository = AppointmentRepository(self.session)
        reminder_repository = ReminderRepository(self.session)
        audit_service = AuditService(self.session)

        now = datetime.now(timezone.utc)
        window_start = now + timedelta(hours=hours_before)
        window_end = window_start + timedelta(minutes=window_minutes)
        appointments = await appointment_repository.list_in_window(date_from=window_start, date_to=window_end)

        created_count = 0
        for appointment in appointments:
            if await reminder_repository.exists_for_appointment(str(appointment.id)):
                continue

            reminder = ReminderEvent(
                appointment_id=to_uuid(str(appointment.id)),
                scheduled_for=appointment.start_time,
            )
            await reminder_repository.create(reminder)
            await audit_service.record_event(
                event_type=AuditEventType.REMINDER_CREATED,
                user_id=str(appointment.patient_id),
                ip_address=None,
                user_agent=None,
                details={"appointment_id": str(appointment.id)},
            )
            created_count += 1

        await self.session.commit()
        return created_count
