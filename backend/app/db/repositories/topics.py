from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Topic


def list_topics(session: Session) -> list[Topic]:
    statement = select(Topic).options(selectinload(Topic.tags)).order_by(Topic.sort_order, Topic.id)
    return list(session.scalars(statement))
