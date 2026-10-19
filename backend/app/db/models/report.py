from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, UtcDateTime, utc_now


class Report(Base):
    __tablename__ = "reports"

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    voter_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"))
    ip_hash: Mapped[str] = mapped_column(String(64))
    reason: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
    resolved_at: Mapped[datetime | None] = mapped_column(UtcDateTime())
