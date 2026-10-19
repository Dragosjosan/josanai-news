from datetime import datetime
from enum import StrEnum

from sqlalchemy import Column, Float, ForeignKey, Index, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.account import Account
from app.db.models.base import Base, UtcDateTime, string_enum, utc_now
from app.db.models.topic import Topic, TopicTag

item_tags = Table(
    "item_tags",
    Base.metadata,
    Column("item_id", ForeignKey("items.id"), primary_key=True),
    Column("tag_id", ForeignKey("topic_tags.id"), primary_key=True),
)


class RelationOrigin(StrEnum):
    SUBMITTED = "submitted"
    JEV = "jev"


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (Index("ix_items_created_at_id", "created_at", "id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(String(2048))
    canonical_url: Mapped[str] = mapped_column(String(2048), unique=True)
    domain: Mapped[str] = mapped_column(String(255))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    publisher: Mapped[str | None] = mapped_column(String(40))
    publisher_key: Mapped[str | None] = mapped_column(String(40), index=True)
    submitter_ip_hash: Mapped[str | None] = mapped_column(String(64), index=True)

    source_name: Mapped[str | None] = mapped_column(String(200))
    published_at: Mapped[datetime | None] = mapped_column(UtcDateTime())
    summary: Mapped[str | None] = mapped_column(Text)
    primary_ref: Mapped[str | None] = mapped_column(String(200))
    provenance_score: Mapped[float | None] = mapped_column(Float)

    upvotes: Mapped[int] = mapped_column(default=0)
    downvotes: Mapped[int] = mapped_column(default=0)
    unique_clicks: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
    deleted_at: Mapped[datetime | None] = mapped_column(UtcDateTime())
    deleted_by_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"))

    topic: Mapped[Topic] = relationship()
    account: Mapped[Account] = relationship(foreign_keys=[account_id])
    tags: Mapped[list[TopicTag]] = relationship(secondary=item_tags, order_by=TopicTag.name)
    corroborating: Mapped[list["ItemCorroboratingUrl"]] = relationship(
        order_by="ItemCorroboratingUrl.position", cascade="all, delete-orphan"
    )
    related: Mapped[list["ItemRelatedUrl"]] = relationship(cascade="all, delete-orphan")


class ItemCorroboratingUrl(Base):
    __tablename__ = "item_corroborating_urls"

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    position: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2048))


class ItemRelatedUrl(Base):
    __tablename__ = "item_related_urls"

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    canonical_url: Mapped[str] = mapped_column(String(2048), primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(2048))
    origin: Mapped[RelationOrigin] = mapped_column(string_enum(RelationOrigin))
