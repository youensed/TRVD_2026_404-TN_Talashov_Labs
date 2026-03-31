from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class ReminderEvent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reminder_events"
    __table_args__ = (
        Index("ix_reminder_events_appointment_id", "appointment_id", unique=True),
    )

    appointment_id: Mapped[str] = mapped_column(ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

