from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Vote


def get(session: Session, item_id: int, ip_hash: str) -> Vote | None:
    return session.scalar(select(Vote).where(Vote.item_id == item_id, Vote.ip_hash == ip_hash))


def voted_item_ids(session: Session, ip_hash: str, item_ids: Sequence[int]) -> set[int]:
    if not item_ids:
        return set()
    statement = select(Vote.item_id).where(Vote.ip_hash == ip_hash, Vote.item_id.in_(item_ids))
    return set(session.scalars(statement))


def recent_votes(session: Session, ip_hash: str, since: datetime) -> tuple[int, datetime | None]:
    statement = select(func.count(), func.min(Vote.created_at)).where(
        Vote.ip_hash == ip_hash, Vote.created_at >= since
    )
    count, oldest = session.execute(statement).one()
    return count, oldest
