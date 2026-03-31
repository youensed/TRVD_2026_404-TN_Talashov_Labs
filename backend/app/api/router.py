from __future__ import annotations

from fastapi import APIRouter

from app.modules.appointments.router import router as appointments_router
from app.modules.auth.router import router as auth_router
from app.modules.doctors.router import router as doctors_router
from app.modules.medical_records.router import router as medical_records_router
from app.modules.payments.router import router as payments_router
from app.modules.reports.router import router as reports_router
from app.modules.schedules.router import router as schedules_router
from app.modules.users.router import router as users_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(doctors_router)
api_router.include_router(schedules_router)
api_router.include_router(appointments_router)
api_router.include_router(medical_records_router)
api_router.include_router(payments_router)
api_router.include_router(reports_router)

