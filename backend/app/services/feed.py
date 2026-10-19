from collections.abc import Callable
from datetime import datetime

from sqlalchemy.orm import Session

from app.config import Settings
from app.db.models import Item, utc_now
from app.db.repositories import items as item_repo
from app.db.repositories import topics as topic_repo
from app.db.repositories.items import FeedFilter, RankCandidate
from app.dto.items import FeedQuery, FeedResponse, ItemSummary
from app.errors import AppError, ErrorCode
from app.services.ranking import ItemStats, RankingSettings, score
from app.services.urls import display_domain


class FeedService:
    def __init__(
        self,
        session: Session,
        settings: Settings,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._session = session
        self._clock = clock
        self._feed_size = settings.feed_size
        self._candidate_limit = settings.rank_candidates
        self._ranking = RankingSettings(
            gravity=settings.rank_gravity,
            click_weight=settings.rank_click_w,
            downvote_penalty=settings.rank_downvote_p,
        )

    def get_front_page(self, query: FeedQuery) -> FeedResponse:
        self._check_filters(query)
        feed_filter = FeedFilter(query.topic, query.tag)
        candidates = item_repo.list_rank_candidates(
            self._session, feed_filter, self._candidate_limit
        )
        item_ids = self._rank(candidates)[: self._feed_size]
        items = item_repo.get_items_in_order(self._session, item_ids)
        comment_counts = item_repo.count_visible_comments(self._session, item_ids)
        return FeedResponse(
            items=[_to_response(item, comment_counts.get(item.id, 0)) for item in items]
        )

    def _check_filters(self, query: FeedQuery) -> None:
        if query.topic is not None and not topic_repo.topic_exists(self._session, query.topic):
            raise AppError(ErrorCode.UNKNOWN_TOPIC, f"Unknown topic '{query.topic}'.")
        if query.tag is not None and not topic_repo.tag_exists(
            self._session, query.tag, query.topic
        ):
            raise AppError(ErrorCode.UNKNOWN_TAG, f"Unknown tag '{query.tag}'.")

    def _rank(self, candidates: list[RankCandidate]) -> list[int]:
        now = self._clock()
        ordered = sorted(
            candidates,
            key=lambda c: (
                score(ItemStats(c.upvotes, c.downvotes, c.created_at), now, self._ranking),
                c.created_at,
                c.id,
            ),
            reverse=True,
        )
        return [c.id for c in ordered]


def _to_response(item: Item, comment_count: int) -> ItemSummary:
    return ItemSummary(
        id=item.id,
        title=item.title,
        url=item.url,
        domain=display_domain(item.url),
        topic=item.topic.slug,
        tags=[tag.name for tag in item.tags],
        score=item.upvotes - item.downvotes,
        comment_count=comment_count,
        publisher=item.publisher,
        created_at=item.created_at,
        viewer_vote=None,
    )
