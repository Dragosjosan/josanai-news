from datetime import datetime
from enum import StrEnum

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, UtcDateTime, string_enum, utc_now


class FlagResolution(StrEnum):
    DISMISSED = "dismissed"
    DELETED = "deleted"


class Flag(Base):
    __tablename__ = "flags"

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), primary_key=True, index=True)
    reason: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
    resolved_at: Mapped[datetime | None] = mapped_column(UtcDateTime(), index=True)
    resolution: Mapped[FlagResolution | None] = mapped_column(string_enum(FlagResolution))
    resolved_by_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"))
