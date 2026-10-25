from datetime import datetime
from enum import StrEnum

from sqlalchemy import Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, UtcDateTime, string_enum, utc_now


class CheckOutcome(StrEnum):
    PUBLISHED = "published"
    HARMFUL = "harmful"
    DUPLICATE = "duplicate"
    UNAVAILABLE = "unavailable"


class SubmissionCheck(Base):
    __tablename__ = "submission_checks"
    __table_args__ = (
        Index("ix_submission_checks_ip_hash_created_at", "ip_hash", "created_at"),
        Index("ix_submission_checks_account_id_created_at", "account_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"))
    ip_hash: Mapped[str | None] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(String(2048))
    outcome: Mapped[CheckOutcome] = mapped_column(string_enum(CheckOutcome))
    harm_probability: Mapped[float | None] = mapped_column(Float)
    duplicate_of_id: Mapped[int | None] = mapped_column(ForeignKey("items.id"))
    duplicate_probability: Mapped[float | None] = mapped_column(Float)
    model: Mapped[str | None] = mapped_column(String(32))
    item_id: Mapped[int | None] = mapped_column(ForeignKey("items.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
