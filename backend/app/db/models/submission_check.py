from datetime import datetime
from enum import StrEnum

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, UtcDateTime, string_enum, utc_now


class CheckOutcome(StrEnum):
    PUBLISHED = "published"
    OFF_TOPIC = "off_topic"
    DUPLICATE = "duplicate"
    UNAVAILABLE = "unavailable"


class StoryRelation(StrEnum):
    SAME = "same"
    UPDATE = "update"
    DIFFERENT = "different"


class SubmissionCheck(Base):
    __tablename__ = "submission_checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    submitter_ip_hash: Mapped[str | None] = mapped_column(String(64))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    title: Mapped[str] = mapped_column(String(300))
    canonical_url: Mapped[str] = mapped_column(String(2048))
    outcome: Mapped[CheckOutcome] = mapped_column(string_enum(CheckOutcome))
    on_topic_probability: Mapped[float | None] = mapped_column(Float)
    relation: Mapped[StoryRelation | None] = mapped_column(string_enum(StoryRelation))
    relation_probability: Mapped[float | None] = mapped_column(Float)
    matched_item_id: Mapped[int | None] = mapped_column(ForeignKey("items.id"))
    shortlist_size: Mapped[int] = mapped_column(default=0)
    model: Mapped[str | None] = mapped_column(String(32))
    item_id: Mapped[int | None] = mapped_column(ForeignKey("items.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now, index=True)
