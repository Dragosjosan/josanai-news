from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.models import Comment, Item, ItemLink, LinkKind, Topic, TopicTag


@dataclass(frozen=True, slots=True)
class FeedFilter:
    topic: str | None = None
    tag: str | None = None


@dataclass(frozen=True, slots=True)
class RankCandidate:
    id: int
    upvotes: int
    downvotes: int
    created_at: datetime


def _visible[*Ts](statement: Select[*Ts], feed_filter: FeedFilter) -> Select[*Ts]:
    statement = statement.where(Item.deleted_at.is_(None))
    if feed_filter.topic is not None:
        statement = statement.join(Topic, Item.topic_id == Topic.id).where(
            Topic.slug == feed_filter.topic
        )
    if feed_filter.tag is not None:
        statement = statement.where(Item.tags.any(TopicTag.name == feed_filter.tag))
    return statement


def list_rank_candidates(
    session: Session, feed_filter: FeedFilter, limit: int
) -> list[RankCandidate]:
    statement = (
        _visible(select(Item.id, Item.upvotes, Item.downvotes, Item.created_at), feed_filter)
        .order_by(Item.created_at.desc(), Item.id.desc())
        .limit(limit)
    )
    return [RankCandidate(*row) for row in session.execute(statement)]


def get_items_in_order(session: Session, ids: Sequence[int]) -> list[Item]:
    if not ids:
        return []
    statement = (
        select(Item)
        .where(Item.id.in_(ids))
        .options(joinedload(Item.topic), joinedload(Item.account), selectinload(Item.tags))
    )
    by_id = {item.id: item for item in session.scalars(statement)}
    return [by_id[item_id] for item_id in ids if item_id in by_id]


def count_visible_comments(session: Session, item_ids: Sequence[int]) -> dict[int, int]:
    if not item_ids:
        return {}
    statement = (
        select(Comment.item_id, func.count())
        .where(Comment.item_id.in_(item_ids), Comment.deleted_at.is_(None))
        .group_by(Comment.item_id)
    )
    return {item_id: count for item_id, count in session.execute(statement)}


def get_by_url(session: Session, url: str) -> Item | None:
    return session.scalar(select(Item).where(Item.url == url))


def get_visible(session: Session, item_id: int) -> Item | None:
    statement = (
        select(Item)
        .where(Item.id == item_id, Item.deleted_at.is_(None))
        .options(
            joinedload(Item.topic),
            joinedload(Item.account),
            selectinload(Item.tags),
            selectinload(Item.links),
        )
    )
    return session.scalar(statement)


def list_earlier(session: Session, item: Item) -> list[Item]:
    related = [link.url for link in item.links if link.kind is LinkKind.RELATED]
    if not related:
        return []
    statement = (
        select(Item)
        .where(Item.url.in_(related), Item.deleted_at.is_(None))
        .order_by(Item.created_at, Item.id)
    )
    return list(session.scalars(statement))


def list_later(session: Session, item: Item) -> list[Item]:
    statement = (
        select(Item)
        .join(ItemLink, ItemLink.item_id == Item.id)
        .where(
            ItemLink.kind == LinkKind.RELATED,
            ItemLink.url == item.url,
            Item.deleted_at.is_(None),
            Item.id != item.id,
        )
        .order_by(Item.created_at, Item.id)
    )
    return list(session.scalars(statement))
