from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, UtcDateTime, utc_now


class Click(Base):
    __tablename__ = "clicks"

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    voter_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
