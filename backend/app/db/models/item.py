from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.account import Account
from app.db.models.base import Base, UtcDateTime, utc_now


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (Index("ix_items_created_at_id", "created_at", "id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(String(2048), unique=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"))
    label: Mapped[str | None] = mapped_column(String(40))
    ip_hash: Mapped[str | None] = mapped_column(String(64))
    source_name: Mapped[str | None] = mapped_column(String(200))
    published_at: Mapped[datetime | None] = mapped_column(UtcDateTime())
    summary: Mapped[str | None] = mapped_column(Text)
    primary_ref: Mapped[str | None] = mapped_column(String(200))
    upvotes: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
    deleted_at: Mapped[datetime | None] = mapped_column(UtcDateTime())

    account: Mapped[Account | None] = relationship()
