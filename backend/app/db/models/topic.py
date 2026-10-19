from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text, default="")
    sort_order: Mapped[int] = mapped_column(default=0)

    tags: Mapped[list["TopicTag"]] = relationship(back_populates="topic", order_by="TopicTag.name")


class TopicTag(Base):
    __tablename__ = "topic_tags"
    __table_args__ = (UniqueConstraint("topic_id", "name", name="uq_topic_tags_topic_id_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), index=True)
    name: Mapped[str] = mapped_column(String(48))

    topic: Mapped[Topic] = relationship(back_populates="tags")
