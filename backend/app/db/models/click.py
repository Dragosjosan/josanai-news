from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, UtcDateTime, utc_now


class ClickEvent(Base):
    __tablename__ = "click_events"
    __table_args__ = (Index("ix_click_events_item_id_voter_id", "item_id", "voter_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    voter_id: Mapped[str] = mapped_column(String(32))
    ip_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)


class ItemImpressionDaily(Base):
    __tablename__ = "item_impressions_daily"

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    day: Mapped[date] = mapped_column(Date, primary_key=True)
    position_bucket: Mapped[int] = mapped_column(primary_key=True)
    count: Mapped[int] = mapped_column(default=0)
