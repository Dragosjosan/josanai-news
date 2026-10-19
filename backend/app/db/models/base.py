from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import Enum, MetaData, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TypeDecorator


def utc_now() -> datetime:
    return datetime.now(UTC)


def string_enum(enum_class: type[StrEnum], length: int = 16) -> Enum:
    return Enum(
        enum_class,
        native_enum=False,
        length=length,
        values_callable=lambda members: [member.value for member in members],
    )


class UtcDateTime(TypeDecorator[datetime]):
    impl = String(24)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Any) -> str | None:
        del dialect
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("UTC datetime fields require a timezone-aware value")
        return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    def process_result_value(self, value: str | None, dialect: Any) -> datetime | None:
        del dialect
        if value is None:
            return None
        return datetime.fromisoformat(value).astimezone(UTC)


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
