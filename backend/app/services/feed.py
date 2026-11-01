from collections.abc import Callable
from datetime import UTC, datetime, time, timedelta

from sqlalchemy.orm import Session

from app.config import Settings
from app.db.models import utc_now
from app.db.repositories import accounts as account_repo
from app.db.repositories import comments as comment_repo
from app.db.repositories import items as item_repo
from app.db.repositories import votes as vote_repo
from app.db.repositories.items import RankCandidate
from app.dto.items import FeedQuery, FeedResponse
from app.services.item_views import to_summary
from app.services.ranking import ItemStats, RankingSettings, score


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
        self._ranking = RankingSettings(gravity=settings.rank_gravity)

    def get_feed(self, query: FeedQuery, ip_hash: str) -> FeedResponse:
        account_id = None
        if query.username is not None:
            account = account_repo.get_by_username(self._session, query.username.lower())
            if account is None:
                return FeedResponse(items=[])
            account_id = account.id
        item_ids = self._item_ids(query, account_id)
        items = item_repo.get_items_in_order(self._session, item_ids)
        voted = vote_repo.voted_item_ids(self._session, ip_hash, item_ids)
        counts = comment_repo.visible_counts(self._session, item_ids)
        return FeedResponse(
            items=[to_summary(item, item.id in voted, counts.get(item.id, 0)) for item in items]
        )

    def _item_ids(self, query: FeedQuery, account_id: int | None) -> list[int]:
        if query.day is not None:
            start = datetime.combine(query.day, time(), tzinfo=UTC)
            return item_repo.list_day_ids(
                self._session,
                start,
                start + timedelta(days=1),
                by_votes=query.sort == "top",
                limit=self._feed_size,
                account_id=account_id,
            )
        if query.sort == "new":
            return item_repo.list_newest_ids(self._session, self._feed_size, account_id)
        candidates = item_repo.list_rank_candidates(
            self._session, self._candidate_limit, account_id
        )
        return self._rank(candidates)[: self._feed_size]

    def _rank(self, candidates: list[RankCandidate]) -> list[int]:
        now = self._clock()
        ordered = sorted(
            candidates,
            key=lambda c: (
                score(ItemStats(c.upvotes, c.created_at), now, self._ranking),
                c.created_at,
                c.id,
            ),
            reverse=True,
        )
        return [c.id for c in ordered]
