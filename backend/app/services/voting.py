from collections.abc import Callable
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.models import Vote, utc_now
from app.db.repositories import items as item_repo
from app.db.repositories import votes as vote_repo
from app.dto.items import VoteRequest, VoteResponse
from app.errors import AppError, ErrorCode
from app.services.identity import Credentials, resolve_identity
from app.services.rate_limits import RATE_WINDOW, check_rate


class VotingService:
    def __init__(
        self,
        session: Session,
        settings: Settings,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._session = session
        self._settings = settings
        self._clock = clock

    def vote(self, item_id: int, request: VoteRequest, credentials: Credentials) -> VoteResponse:
        identity = resolve_identity(self._session, credentials)
        self._require_item(item_id)
        existing = vote_repo.get(self._session, item_id, identity.ip_hash)
        if request.direction == "up" and existing is None:
            self._check_rate(identity.ip_hash)
            self._session.add(
                Vote(
                    item_id=item_id,
                    ip_hash=identity.ip_hash,
                    account_id=identity.account.id if identity.account else None,
                )
            )
            try:
                self._session.flush()
            except IntegrityError:
                self._session.rollback()
            else:
                item_repo.add_upvotes(self._session, item_id, 1)
        elif request.direction == "none" and existing is not None:
            self._session.delete(existing)
            item_repo.add_upvotes(self._session, item_id, -1)
        self._session.commit()
        return VoteResponse(
            score=self._require_item(item_id),
            viewer_vote="up" if request.direction == "up" else None,
        )

    def _require_item(self, item_id: int) -> int:
        upvotes = item_repo.get_visible_upvotes(self._session, item_id)
        if upvotes is None:
            raise AppError(ErrorCode.NOT_FOUND, "Item not found.")
        return upvotes

    def _check_rate(self, ip_hash: str) -> None:
        now = self._clock()
        count, oldest = vote_repo.recent_votes(self._session, ip_hash, now - RATE_WINDOW)
        check_rate(count, oldest, self._settings.vote_per_hour, now, "votes")
