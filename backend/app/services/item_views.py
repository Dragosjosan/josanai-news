from sqlalchemy.orm import Session

from app.db.models import Item, LinkKind
from app.db.repositories import comments as comment_repo
from app.db.repositories import items as item_repo
from app.dto.items import ItemDetail, ItemRef, ItemSummary, Link
from app.services.urls import display_domain


def to_summary(item: Item, voted: bool, comment_count: int) -> ItemSummary:
    return ItemSummary(
        id=item.id,
        title=item.title,
        url=item.url,
        domain=display_domain(item.url),
        summary=item.summary,
        score=item.upvotes,
        comment_count=comment_count,
        username=item.account.username if item.account else None,
        label=item.label,
        created_at=item.created_at,
        viewer_vote="up" if voted else None,
    )


def to_detail(session: Session, item: Item, voted: bool) -> ItemDetail:
    return ItemDetail(
        **to_summary(
            item, voted, comment_repo.visible_counts(session, [item.id]).get(item.id, 0)
        ).model_dump(),
        source_name=item.source_name,
        published_at=item.published_at,
        primary_ref=item.primary_ref,
        corroborating=[
            Link(url=link.url, domain=display_domain(link.url))
            for link in item.links
            if link.kind is LinkKind.CORROBORATING
        ],
        earlier=[_ref(other) for other in item_repo.list_earlier(session, item)],
        later=[_ref(other) for other in item_repo.list_later(session, item)],
        viewer_reported=False,
    )


def _ref(item: Item) -> ItemRef:
    return ItemRef(
        id=item.id,
        title=item.title,
        domain=display_domain(item.url),
        created_at=item.created_at,
    )
