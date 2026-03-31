from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.modules.common.enums import AppointmentStatus


class Appointment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_start_time", "start_time"),
        Index("ix_appointments_doctor_id", "doctor_id"),
        Index(
            "uq_appointments_doctor_active_slot",
            "doctor_id",
            "start_time",
            unique=True,
            postgresql_where=text("status IN ('SCHEDULED', 'COMPLETED', 'NO_SHOW')"),
        ),
        Index(
            "uq_appointments_patient_active_slot",
            "patient_id",
            "start_time",
            unique=True,
            postgresql_where=text("status IN ('SCHEDULED', 'COMPLETED', 'NO_SHOW')"),
        ),
    )

    patient_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    doctor_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, native_enum=False),
        nullable=False,
        default=AppointmentStatus.SCHEDULED,
    )

    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_appointments")
    medical_record = relationship("MedicalRecord", back_populates="appointment", uselist=False)
    payment = relationship("Payment", back_populates="appointment", uselist=False)

