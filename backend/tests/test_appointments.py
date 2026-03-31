from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.modules.appointments.model import Appointment
from app.modules.common.enums import AppointmentStatus, UserRole

from .conftest import TestSessionFactory
from .helpers import create_shift, create_user, login


async def test_duplicate_appointment_booking_is_rejected(client):  # noqa: ANN001
    doctor = await create_user(
        email="doctor@example.com",
        password="Doctor123!",
        role=UserRole.DOCTOR,
        first_name="Олег",
        last_name="Лікар",
        phone="+380670000010",
        specialty="Кардіологія",
    )
    await create_user(
        email="patient@example.com",
        password="Patient123!",
        role=UserRole.PATIENT,
        first_name="Марта",
        last_name="Пацієнт",
        phone="+380670000011",
    )
    start_time = datetime.now(timezone.utc).replace(second=0, microsecond=0) + timedelta(days=1, hours=2)
    await create_shift(str(doctor.id), start_time, start_time + timedelta(hours=2))

    await login(client, "patient@example.com", "Patient123!")
    csrf_token = client.cookies.get("csrf_token")

    first_response = await client.post(
        "/appointments",
        json={"doctor_id": str(doctor.id), "start_time": start_time.isoformat()},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert first_response.status_code == 201

    second_response = await client.post(
        "/appointments",
        json={"doctor_id": str(doctor.id), "start_time": start_time.isoformat()},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert second_response.status_code == 409


async def test_patient_cannot_cancel_less_than_two_hours_before_visit(client):  # noqa: ANN001
    doctor = await create_user(
        email="doctor-short@example.com",
        password="Doctor123!",
        role=UserRole.DOCTOR,
        first_name="Олена",
        last_name="Лікар",
        phone="+380670000012",
        specialty="Терапія",
    )
    patient = await create_user(
        email="patient-short@example.com",
        password="Patient123!",
        role=UserRole.PATIENT,
        first_name="Назар",
        last_name="Пацієнт",
        phone="+380670000013",
    )

    async with TestSessionFactory() as session:
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            start_time=datetime.now(timezone.utc) + timedelta(hours=1),
            end_time=datetime.now(timezone.utc) + timedelta(hours=1, minutes=30),
            status=AppointmentStatus.SCHEDULED,
        )
        session.add(appointment)
        await session.commit()
        appointment_id = str(appointment.id)

    await login(client, "patient-short@example.com", "Patient123!")
    csrf_token = client.cookies.get("csrf_token")

    response = await client.patch(
        f"/appointments/{appointment_id}/cancel",
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400
