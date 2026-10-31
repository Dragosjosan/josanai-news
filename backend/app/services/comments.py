from collections.abc import Callable
from datetime import datetime

from sqlalchemy.orm import Session

from app.clients.jev import JevClient, JevUnavailableError
from app.config import Settings
from app.db.models import Comment, CommentCheck, CommentCheckOutcome, utc_now
from app.db.repositories import comments as comment_repo
from app.db.repositories import items as item_repo
from app.dto.comments import CommentResponse, SubmitCommentRequest, ThreadResponse
from app.errors import AppError, ErrorCode
from app.services.identity import Credentials, Identity, resolve_identity
from app.services.moderation import judge_comment
from app.services.rate_limits import RATE_WINDOW, check_rate


class CommentService:
    def __init__(
        self,
        session: Session,
        settings: Settings,
        jev: JevClient,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._session = session
        self._settings = settings
        self._jev = jev
        self._clock = clock

    def thread(self, item_id: int, credentials: Credentials) -> ThreadResponse:
        identity = resolve_identity(self._session, credentials)
        self._require_item(item_id)
        return ThreadResponse(
            comments=[
                _view(comment, identity)
                for comment in comment_repo.list_thread(self._session, item_id)
            ]
        )

    def submit(
        self, item_id: int, request: SubmitCommentRequest, credentials: Credentials
    ) -> CommentResponse:
        identity = resolve_identity(self._session, credentials)
        if identity.account is None and self._settings.comment_requires_account:
            raise AppError(
                ErrorCode.NOT_AUTHENTICATED,
                "This site requires an account to comment. Log in or send an X-API-Key header.",
            )
        self._require_item(item_id)
        self._require_parent(item_id, request.parent_id)
        self._check_rate(identity)
        check = self._judge(item_id, request, identity)
        # Moderation can take seconds; the target must still exist when we publish.
        self._require_item(item_id)
        self._require_parent(item_id, request.parent_id)
        assert identity.voter_id is not None
        comment = Comment(
            item_id=item_id,
            parent_id=request.parent_id,
            account_id=identity.account.id if identity.account else None,
            voter_id=identity.voter_id,
            ip_hash=identity.ip_hash,
            text=request.text,
            created_at=self._clock(),
        )
        check.outcome = CommentCheckOutcome.PUBLISHED
        self._session.add(comment)
        self._session.flush()
        check.comment_id = comment.id
        self._session.add(check)
        self._session.commit()
        created = comment_repo.get(self._session, comment.id)
        assert created is not None
        return _view(created, identity)

    def delete(self, comment_id: int, credentials: Credentials) -> None:
        identity = resolve_identity(self._session, credentials)
        comment = comment_repo.get(self._session, comment_id)
        if comment is None:
            raise AppError(ErrorCode.NOT_FOUND, "Comment not found.")
        self._require_item(comment.item_id)
        if not _can_delete(comment, identity):
            raise AppError(ErrorCode.FORBIDDEN, "You cannot delete this comment.")
        if comment.deleted_at is None:
            comment.deleted_at = self._clock()
            self._session.commit()

    def _require_item(self, item_id: int) -> None:
        if item_repo.get_visible_upvotes(self._session, item_id) is None:
            raise AppError(ErrorCode.NOT_FOUND, "Item not found.")

    def _require_parent(self, item_id: int, parent_id: int | None) -> None:
        if (
            parent_id is not None
            and comment_repo.get_parent(self._session, item_id, parent_id) is None
        ):
            raise AppError(
                ErrorCode.PARENT_NOT_FOUND, "The parent comment is not available on this item."
            )

    def _check_rate(self, identity: Identity) -> None:
        now = self._clock()
        count, oldest = comment_repo.recent_attempts(
            self._session,
            identity.account.id if identity.account else None,
            identity.ip_hash,
            now - RATE_WINDOW,
        )
        check_rate(count, oldest, self._settings.comment_per_hour, now, "comments")

    def _judge(
        self, item_id: int, request: SubmitCommentRequest, identity: Identity
    ) -> CommentCheck:
        check = CommentCheck(
            item_id=item_id,
            parent_id=request.parent_id,
            account_id=identity.account.id if identity.account else None,
            ip_hash=identity.ip_hash,
            text=request.text,
            created_at=self._clock(),
        )
        try:
            verdict = judge_comment(self._jev, request.text)
        except JevUnavailableError as error:
            check.outcome = CommentCheckOutcome.UNAVAILABLE
            self._save_check(check)
            raise AppError(
                ErrorCode.JEV_UNAVAILABLE,
                "The moderation check is unavailable. Try again later.",
                retry_after=self._settings.jev_retry_after_seconds,
            ) from error
        check.model = verdict.model
        check.harm_probability = verdict.harm_probability
        if verdict.harm_probability >= self._settings.jev_harmful_min:
            check.outcome = CommentCheckOutcome.HARMFUL
            self._save_check(check)
            raise AppError(ErrorCode.HARMFUL_CONTENT, "The comment contains harmful language.")
        return check

    def _save_check(self, check: CommentCheck) -> None:
        self._session.add(check)
        self._session.commit()


def _can_delete(comment: Comment, identity: Identity) -> bool:
    if identity.account is not None and (
        identity.account.is_admin or comment.account_id == identity.account.id
    ):
        return True
    return (
        comment.account_id is None
        and identity.voter_id is not None
        and comment.voter_id == identity.voter_id
    )


def _view(comment: Comment, identity: Identity) -> CommentResponse:
    deleted = comment.deleted_at is not None
    return CommentResponse(
        id=comment.id,
        parent_id=comment.parent_id,
        author=comment.account.username if comment.account is not None and not deleted else None,
        text=comment.text if not deleted else None,
        created_at=comment.created_at,
        deleted=deleted,
        can_delete=_can_delete(comment, identity),
    )
