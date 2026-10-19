from datetime import datetime
from enum import StrEnum

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, UtcDateTime, string_enum, utc_now

ANONYMOUS_USERNAME = "anonymous"


class AccountKind(StrEnum):
    HUMAN = "human"
    AGENT = "agent"
    ADMIN = "admin"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    username_key: Mapped[str] = mapped_column(String(32), unique=True)
    kind: Mapped[AccountKind] = mapped_column(string_enum(AccountKind))
    publisher_name: Mapped[str | None] = mapped_column(String(40))
    publisher_key: Mapped[str | None] = mapped_column(String(40), unique=True)
    api_key_hash: Mapped[str | None] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
    deleted_at: Mapped[datetime | None] = mapped_column(UtcDateTime())


class AccountSession(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(UtcDateTime())
