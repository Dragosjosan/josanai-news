from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.account import Account
from app.db.models.base import Base, UtcDateTime, utc_now


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (Index("ix_comments_item_id_created_at_id", "item_id", "created_at", "id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"))
    voter_id: Mapped[str] = mapped_column(String(64))
    ip_hash: Mapped[str] = mapped_column(String(64))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
    deleted_at: Mapped[datetime | None] = mapped_column(UtcDateTime())

    account: Mapped[Account | None] = relationship()
