from datetime import datetime
from enum import StrEnum

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, UtcDateTime, string_enum, utc_now


class RateAction(StrEnum):
    SUBMIT = "submit"
    VOTE = "vote"
    CLICK = "click"
    COMMENT = "comment"
    FLAG = "flag"
    SIGNUP = "signup"
    LOGIN = "login"


class RateEvent(Base):
    __tablename__ = "rate_events"
    __table_args__ = (Index("ix_rate_events_action_key_created_at", "action", "key", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[RateAction] = mapped_column(string_enum(RateAction))
    key: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
