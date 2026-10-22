from datetime import datetime

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, UtcDateTime, utc_now


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (Index("ix_votes_ip_hash_created_at", "ip_hash", "created_at"),)

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    ip_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
