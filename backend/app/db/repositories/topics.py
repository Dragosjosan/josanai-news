from sqlalchemy import exists, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Topic, TopicTag


def list_topics(session: Session) -> list[Topic]:
    statement = select(Topic).options(selectinload(Topic.tags)).order_by(Topic.id)
    return list(session.scalars(statement))


def topic_exists(session: Session, slug: str) -> bool:
    return bool(session.scalar(select(exists().where(Topic.slug == slug))))


def tag_exists(session: Session, name: str, topic_slug: str | None = None) -> bool:
    condition = TopicTag.name == name
    if topic_slug is not None:
        condition = condition & TopicTag.topic.has(Topic.slug == topic_slug)
    return bool(session.scalar(select(exists().where(condition))))
