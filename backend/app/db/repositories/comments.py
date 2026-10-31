from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import Comment, CommentCheck


def get(session: Session, comment_id: int) -> Comment | None:
    return session.scalar(
        select(Comment).where(Comment.id == comment_id).options(joinedload(Comment.account))
    )


def get_parent(session: Session, item_id: int, parent_id: int) -> Comment | None:
    return session.scalar(
        select(Comment).where(
            Comment.id == parent_id,
            Comment.item_id == item_id,
            Comment.deleted_at.is_(None),
        )
    )


def list_thread(session: Session, item_id: int) -> list[Comment]:
    statement = (
        select(Comment)
        .where(Comment.item_id == item_id)
        .options(joinedload(Comment.account))
        .order_by(Comment.created_at, Comment.id)
    )
    return list(session.scalars(statement))


def visible_counts(session: Session, item_ids: Sequence[int]) -> dict[int, int]:
    if not item_ids:
        return {}
    statement = (
        select(Comment.item_id, func.count())
        .where(Comment.item_id.in_(item_ids), Comment.deleted_at.is_(None))
        .group_by(Comment.item_id)
    )
    return {item_id: count for item_id, count in session.execute(statement)}


def recent_attempts(
    session: Session, account_id: int | None, ip_hash: str, since: datetime
) -> tuple[int, datetime | None]:
    by_author = (
        CommentCheck.account_id == account_id
        if account_id is not None
        else CommentCheck.ip_hash == ip_hash
    )
    statement = select(func.count(), func.min(CommentCheck.created_at)).where(
        by_author, CommentCheck.created_at >= since
    )
    count, oldest = session.execute(statement).one()
    return count, oldest
