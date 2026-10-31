from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Comment, Item, Report


def get(session: Session, report_id: int) -> Report | None:
    return session.get(Report, report_id)


def list_open(session: Session) -> list[Report]:
    statement = (
        select(Report)
        .join(Item, Report.item_id == Item.id)
        .outerjoin(Comment, Report.comment_id == Comment.id)
        .where(
            Report.hidden_at.is_(None),
            Item.deleted_at.is_(None),
            Comment.deleted_at.is_(None),
        )
        .order_by(Report.created_at.desc(), Report.id.desc())
    )
    return list(session.scalars(statement))
