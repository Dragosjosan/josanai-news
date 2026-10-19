from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, UtcDateTime, utc_now


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (
        CheckConstraint("direction IN (-1, 1)", name="direction"),
        Index("ix_votes_item_id_ip_hash", "item_id", "ip_hash"),
    )

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    voter_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    ip_hash: Mapped[str] = mapped_column(String(64))
    direction: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)


class VoteEvent(Base):
    __tablename__ = "vote_events"
    __table_args__ = (CheckConstraint("direction IN (-1, 0, 1)", name="direction"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    voter_id: Mapped[str] = mapped_column(String(32))
    ip_hash: Mapped[str] = mapped_column(String(64))
    direction: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
