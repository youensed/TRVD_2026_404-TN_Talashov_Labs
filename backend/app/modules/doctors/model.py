from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class DoctorProfile(UUIDMixin, Base):
    __tablename__ = "doctor_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    specialty: Mapped[str] = mapped_column(String(120), nullable=False)
    cabinet_number: Mapped[str] = mapped_column(String(30), nullable=False)
    bio: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    user = relationship("User", back_populates="doctor_profile")
