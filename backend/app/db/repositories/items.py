from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload

from app.db.models import Item


@dataclass(frozen=True, slots=True)
class RankCandidate:
    id: int
    upvotes: int
    created_at: datetime


@dataclass(frozen=True, slots=True)
class SearchRow:
    id: int
    title: str
    url: str
    created_at: datetime


def list_rank_candidates(session: Session, limit: int) -> list[RankCandidate]:
    statement = (
        select(Item.id, Item.upvotes, Item.created_at)
        .where(Item.deleted_at.is_(None))
        .order_by(Item.created_at.desc(), Item.id.desc())
        .limit(limit)
    )
    return [RankCandidate(*row) for row in session.execute(statement)]


def list_newest_ids(session: Session, limit: int) -> list[int]:
    statement = (
        select(Item.id)
        .where(Item.deleted_at.is_(None))
        .order_by(Item.created_at.desc(), Item.id.desc())
        .limit(limit)
    )
    return list(session.scalars(statement))


def list_day_ids(
    session: Session, start: datetime, end: datetime, by_votes: bool, limit: int
) -> list[int]:
    order = (Item.upvotes.desc(),) if by_votes else ()
    statement = (
        select(Item.id)
        .where(Item.deleted_at.is_(None), Item.created_at >= start, Item.created_at < end)
        .order_by(*order, Item.created_at.desc(), Item.id.desc())
        .limit(limit)
    )
    return list(session.scalars(statement))


def list_search_rows(session: Session) -> list[SearchRow]:
    statement = select(Item.id, Item.title, Item.url, Item.created_at).where(
        Item.deleted_at.is_(None)
    )
    return [SearchRow(*row) for row in session.execute(statement)]


def get_items_in_order(session: Session, ids: Sequence[int]) -> list[Item]:
    if not ids:
        return []
    statement = select(Item).where(Item.id.in_(ids)).options(joinedload(Item.account))
    by_id = {item.id: item for item in session.scalars(statement)}
    return [by_id[item_id] for item_id in ids if item_id in by_id]


def get_by_url(session: Session, url: str) -> Item | None:
    return session.scalar(select(Item).where(Item.url == url))


def get(session: Session, item_id: int) -> Item | None:
    return session.get(Item, item_id)


def visible_by_ip_hash(session: Session, ip_hash: str) -> list[Item]:
    statement = select(Item).where(Item.ip_hash == ip_hash, Item.deleted_at.is_(None))
    return list(session.scalars(statement))


def visible_by_account(session: Session, account_id: int) -> list[Item]:
    statement = select(Item).where(Item.account_id == account_id, Item.deleted_at.is_(None))
    return list(session.scalars(statement))


def get_visible(session: Session, item_id: int) -> Item | None:
    statement = (
        select(Item)
        .where(Item.id == item_id, Item.deleted_at.is_(None))
        .options(joinedload(Item.account))
    )
    return session.scalar(statement)


def get_visible_upvotes(session: Session, item_id: int) -> int | None:
    return session.scalar(select(Item.upvotes).where(Item.id == item_id, Item.deleted_at.is_(None)))


def add_upvotes(session: Session, item_id: int, delta: int) -> None:
    session.execute(update(Item).where(Item.id == item_id).values(upvotes=Item.upvotes + delta))
