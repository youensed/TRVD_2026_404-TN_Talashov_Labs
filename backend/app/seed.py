from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionFactory
from app.modules.appointments.model import Appointment
from app.modules.common.enums import AppointmentStatus, PaymentMethod, PaymentStatus, UserRole
from app.modules.doctors.model import DoctorProfile
from app.modules.medical_records.model import MedicalRecord
from app.modules.payments.model import Payment
from app.modules.schedules.model import ScheduleShift
from app.modules.users.model import User


async def seed() -> None:
    settings = get_settings()
    if not settings.seed_demo_data:
        return

    async with SessionFactory() as session:
        users_result = await session.scalars(select(User))
        existing_users = {user.email: user for user in users_result.all() if user.email}

        owner = existing_users.get("owner@pmc-demo.com")
        if owner is None:
            owner = User(
                email="owner@pmc-demo.com",
                password_hash=hash_password("Owner123!"),
                role=UserRole.OWNER,
                first_name="Ганна",
                last_name="Коваленко",
                phone="+380670000001",
                is_verified=True,
            )
            session.add(owner)

        admin = existing_users.get("admin@pmc-demo.com")
        if admin is None:
            admin = User(
                email="admin@pmc-demo.com",
                password_hash=hash_password("Admin123!"),
                role=UserRole.ADMIN,
                first_name="Марія",
                last_name="Савчук",
                phone="+380670000002",
                is_verified=True,
            )
            session.add(admin)

        doctor = existing_users.get("doctor@pmc-demo.com")
        if doctor is None:
            doctor = User(
                email="doctor@pmc-demo.com",
                password_hash=hash_password("Doctor123!"),
                role=UserRole.DOCTOR,
                first_name="Олег",
                last_name="Мельник",
                phone="+380670000003",
                is_verified=True,
            )
            session.add(doctor)

        patient = existing_users.get("patient@pmc-demo.com")
        if patient is None:
            patient = User(
                email="patient@pmc-demo.com",
                password_hash=hash_password("Patient123!"),
                role=UserRole.PATIENT,
                first_name="Ірина",
                last_name="Шевченко",
                phone="+380670000004",
                is_verified=True,
            )
            session.add(patient)

        await session.flush()

        doctor_profile = await session.scalar(select(DoctorProfile).where(DoctorProfile.user_id == doctor.id))
        if doctor_profile is None:
            doctor_profile = DoctorProfile(
                user_id=doctor.id,
                specialty="Сімейна медицина",
                cabinet_number="12",
                bio="Понад 10 років допомагає пацієнтам із щоденними запитами та профілактикою.",
            )
            session.add(doctor_profile)

        shift_start = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        shift_end = shift_start + timedelta(hours=6)

        existing_shift = await session.scalar(
            select(ScheduleShift).where(ScheduleShift.doctor_id == doctor.id, ScheduleShift.start_time == shift_start)
        )
        if existing_shift is None:
            session.add(
                ScheduleShift(
                    doctor_id=doctor.id,
                    start_time=shift_start,
                    end_time=shift_end,
                    slot_minutes=30,
                    is_active=True,
                )
            )

        await session.flush()

        appointment = await session.scalar(
            select(Appointment).where(Appointment.patient_id == patient.id, Appointment.doctor_id == doctor.id)
        )
        if appointment is None:
            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                start_time=shift_start + timedelta(hours=1),
                end_time=shift_start + timedelta(hours=1, minutes=30),
                status=AppointmentStatus.SCHEDULED,
            )
            session.add(appointment)
            await session.flush()

        completed_appointment = await session.scalar(
            select(Appointment).where(
                Appointment.patient_id == patient.id,
                Appointment.status == AppointmentStatus.COMPLETED,
            )
        )
        if completed_appointment is None:
            completed_appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                start_time=shift_start - timedelta(days=2),
                end_time=shift_start - timedelta(days=2) + timedelta(minutes=30),
                status=AppointmentStatus.COMPLETED,
            )
            session.add(completed_appointment)
            await session.flush()

            session.add(
                MedicalRecord(
                    appointment_id=completed_appointment.id,
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    complaints="Періодичний головний біль та втома.",
                    diagnosis="Легка перевтома без ускладнень.",
                    treatment_plan="Нормалізація режиму сну, контроль тиску, повторний огляд за потреби.",
                )
            )
            session.add(
                Payment(
                    appointment_id=completed_appointment.id,
                    patient_id=patient.id,
                    amount=850,
                    currency="UAH",
                    status=PaymentStatus.PAID,
                    method=PaymentMethod.CARD,
                )
            )

        await session.commit()


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()
