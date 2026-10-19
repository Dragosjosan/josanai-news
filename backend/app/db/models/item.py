from datetime import datetime
from enum import StrEnum

from sqlalchemy import Column, ForeignKey, Index, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, UtcDateTime, string_enum, utc_now
from app.db.models.topic import Topic, TopicTag

item_tags = Table(
    "item_tags",
    Base.metadata,
    Column("item_id", ForeignKey("items.id"), primary_key=True),
    Column("tag_id", ForeignKey("topic_tags.id"), primary_key=True),
)


class LinkKind(StrEnum):
    CORROBORATING = "corroborating"
    RELATED = "related"


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (Index("ix_items_created_at_id", "created_at", "id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(String(2048))
    canonical_url: Mapped[str] = mapped_column(String(2048), unique=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), index=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"))
    publisher: Mapped[str | None] = mapped_column(String(40))
    ip_hash: Mapped[str | None] = mapped_column(String(64))
    source_name: Mapped[str | None] = mapped_column(String(200))
    published_at: Mapped[datetime | None] = mapped_column(UtcDateTime())
    summary: Mapped[str | None] = mapped_column(Text)
    primary_ref: Mapped[str | None] = mapped_column(String(200))
    upvotes: Mapped[int] = mapped_column(default=0)
    downvotes: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(), default=utc_now)
    deleted_at: Mapped[datetime | None] = mapped_column(UtcDateTime())

    topic: Mapped[Topic] = relationship()
    tags: Mapped[list[TopicTag]] = relationship(secondary=item_tags, order_by=TopicTag.name)
    links: Mapped[list["ItemLink"]] = relationship(
        order_by="ItemLink.id", cascade="all, delete-orphan"
    )


class ItemLink(Base):
    __tablename__ = "item_links"
    __table_args__ = (
        UniqueConstraint("item_id", "kind", "url", name="uq_item_links_item_id_kind_url"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    kind: Mapped[LinkKind] = mapped_column(string_enum(LinkKind))
    url: Mapped[str] = mapped_column(String(2048), index=True)
