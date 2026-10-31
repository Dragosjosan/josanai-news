import re

from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.repositories import comments as comment_repo
from app.db.repositories import items as item_repo
from app.db.repositories import votes as vote_repo
from app.db.repositories.items import SearchRow
from app.dto.items import SearchQuery, SearchResponse
from app.services.item_views import to_summary
from app.services.urls import display_domain

MAX_QUERY_WORDS = 16
MIN_FUZZY_LENGTH = 4
MIN_WORD_SCORE = 80.0

_WORD = re.compile(r"\w+")


def words_of(text: str) -> list[str]:
    return list(dict.fromkeys(word.lower() for word in _WORD.findall(text)))


def word_score(query_word: str, word: str) -> float:
    if word.startswith(query_word):
        return 100.0
    if len(query_word) < MIN_FUZZY_LENGTH:
        return 0.0
    return fuzz.ratio(query_word, word)


def match_score(query_words: list[str], row: SearchRow) -> float | None:
    words = words_of(f"{row.title} {display_domain(row.url)}")
    total = 0.0
    for query_word in query_words:
        best = max((word_score(query_word, word) for word in words), default=0.0)
        if best < MIN_WORD_SCORE:
            return None
        total += best
    return total / len(query_words)


class SearchService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self._session = session
        self._page_size = settings.feed_size

    def search(self, query: SearchQuery, ip_hash: str) -> SearchResponse:
        query_words = words_of(query.q)[:MAX_QUERY_WORDS]
        if not query_words:
            return SearchResponse(items=[], page=query.page, has_more=False)
        scored = [
            (score, row)
            for row in item_repo.list_search_rows(self._session)
            if (score := match_score(query_words, row)) is not None
        ]
        scored.sort(key=lambda pair: (pair[0], pair[1].created_at, pair[1].id), reverse=True)
        start = (query.page - 1) * self._page_size
        item_ids = [row.id for _, row in scored[start : start + self._page_size]]
        items = item_repo.get_items_in_order(self._session, item_ids)
        voted = vote_repo.voted_item_ids(self._session, ip_hash, item_ids)
        counts = comment_repo.visible_counts(self._session, item_ids)
        return SearchResponse(
            items=[to_summary(item, item.id in voted, counts.get(item.id, 0)) for item in items],
            page=query.page,
            has_more=len(scored) > start + self._page_size,
        )
