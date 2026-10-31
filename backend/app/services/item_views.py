from sqlalchemy.orm import Session

from app.db.models import Item
from app.db.repositories import comments as comment_repo
from app.dto.items import ItemDetail, ItemSummary
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
    )
