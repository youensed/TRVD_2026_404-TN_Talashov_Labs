from __future__ import annotations

from functools import lru_cache

from cryptography.fernet import Fernet
from sqlalchemy import String, Text, TypeDecorator

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_fernet() -> Fernet:
    return Fernet(get_settings().encryption_key.encode("utf-8"))


class EncryptedString(TypeDecorator[str]):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect: object) -> str | None:
        if value is None:
            return None
        token = get_fernet().encrypt(value.encode("utf-8"))
        return token.decode("utf-8")

    def process_result_value(self, value: str | None, dialect: object) -> str | None:
        if value is None:
            return None
        decrypted = get_fernet().decrypt(value.encode("utf-8"))
        return decrypted.decode("utf-8")


class EncryptedShortString(EncryptedString):
    impl = String(512)

