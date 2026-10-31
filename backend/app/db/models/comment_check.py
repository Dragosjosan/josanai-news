from datetime import datetime
from enum import StrEnum

from sqlalchemy import Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, UtcDateTime, string_enum, utc_now


class CommentCheckOutcome(StrEnum):
    PUBLISHED = "published"
    HARMFUL = "harmful"
    UNAVAILABLE = "unavailable"


class CommentCheck(Base):
    __tablename__ = "comment_checks"
    __table_args__ = (
        Index("ix_comment_checks_ip_hash_created_at", "ip_hash", "created_at"),
        Index("ix_comment_checks_account_id_created_at", "account_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"))
    ip_hash: Mapped[str] = mapped_column(String(64))
    text: Mapped[str] = mapped_column(Text)
    outcome: Mapped[CommentCheckOutcome] = mapped_column(string_enum(CommentCheckOutcome))
    harm_probability: Mapped[float | None] = mapped_column(Float)
    model: Mapped[str | None] = mapped_column(String(32))
    comment_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
