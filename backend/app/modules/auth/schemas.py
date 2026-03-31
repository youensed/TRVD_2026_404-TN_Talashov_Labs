from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.modules.users.schemas import CurrentUserResponse


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=2, max_length=80)
    last_name: str = Field(min_length=2, max_length=80)
    phone: str | None = Field(default=None, max_length=32)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthSessionResponse(BaseModel):
    message: str
    user: CurrentUserResponse


class LogoutResponse(BaseModel):
    message: str

