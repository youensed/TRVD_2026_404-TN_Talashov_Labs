from __future__ import annotations

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.encrypted_type import EncryptedString


class MedicalRecord(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "medical_records"
    __table_args__ = (
        Index("ix_medical_records_patient_id", "patient_id"),
    )

    appointment_id: Mapped[str] = mapped_column(ForeignKey("appointments.id", ondelete="CASCADE"), unique=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    doctor_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    complaints: Mapped[str] = mapped_column(EncryptedString, nullable=False)
    diagnosis: Mapped[str] = mapped_column(EncryptedString, nullable=False)
    treatment_plan: Mapped[str] = mapped_column(EncryptedString, nullable=False)

    appointment = relationship("Appointment", back_populates="medical_record")

