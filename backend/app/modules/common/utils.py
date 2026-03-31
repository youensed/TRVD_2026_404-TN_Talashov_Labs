from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID


def to_uuid(value: str | UUID | None) -> UUID | None:
    if value is None or isinstance(value, UUID):
        return value
    return UUID(value)


def to_uuid_list(values: list[str] | list[UUID]) -> list[UUID]:
    return [value if isinstance(value, UUID) else UUID(value) for value in values]


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
