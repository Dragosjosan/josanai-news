from datetime import datetime
from enum import StrEnum

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, UtcDateTime, string_enum, utc_now


class AccountKind(StrEnum):
    USER = "user"
    AGENT = "agent"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    kind: Mapped[AccountKind] = mapped_column(string_enum(AccountKind))
    is_admin: Mapped[bool] = mapped_column(default=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    api_key_hash: Mapped[str | None] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)


class AccountSession(Base):
    __tablename__ = "sessions"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    expires_at: Mapped[datetime] = mapped_column(UtcDateTime())
