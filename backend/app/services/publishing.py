from collections.abc import Callable
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.clients.jev import JevClient, JevUnavailableError
from app.config import Settings
from app.db.models import (
    CheckOutcome,
    Item,
    ItemLink,
    LinkKind,
    SubmissionCheck,
    utc_now,
)
from app.db.repositories import items as item_repo
from app.db.repositories import search as search_repo
from app.db.repositories import submission_checks as check_repo
from app.dto.items import ItemDetail, SubmitItemRequest
from app.errors import AppError, ErrorCode
from app.services.identity import Credentials, Identity, resolve_identity
from app.services.item_views import to_detail
from app.services.moderation import Submission, Verdict, judge
from app.services.rate_limits import RATE_WINDOW, check_rate
from app.services.urls import display_domain

CONTRACT_VERSION = "1"


class PublishingService:
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

    def submit(self, request: SubmitItemRequest, credentials: Credentials) -> ItemDetail:
        if request.contract_version != CONTRACT_VERSION:
            raise AppError(
                ErrorCode.UNSUPPORTED_CONTRACT_VERSION,
                f"contract_version must be '{CONTRACT_VERSION}'.",
            )
        identity = self._identity(credentials)
        self._check_rate(identity)
        self._check_label(request.label, identity)
        self._reject_known_url(request.url)
        check = self._judge(request, identity)
        return self._insert(request, identity, check)

    def _identity(self, credentials: Credentials) -> Identity:
        identity = resolve_identity(self._session, credentials)
        if identity.account is None and self._settings.post_requires_account:
            raise AppError(
                ErrorCode.NOT_AUTHENTICATED,
                "This site requires an account to post. Log in or send an X-API-Key header.",
            )
        return identity

    def _check_rate(self, identity: Identity) -> None:
        now = self._clock()
        account_id = identity.account.id if identity.account else None
        count, oldest = check_repo.recent_attempts(
            self._session, account_id, identity.ip_hash, now - RATE_WINDOW
        )
        check_rate(count, oldest, self._settings.submit_per_hour, now, "submissions")

    def _check_label(self, label: str | None, identity: Identity) -> None:
        if label is not None and identity.account is None:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                "Only accounts can set a label.",
                {
                    "fields": [
                        {"loc": ["body", "label"], "message": "only accounts can set a label"}
                    ]
                },
            )

    def _reject_known_url(self, url: str) -> None:
        existing = item_repo.get_by_url(self._session, url)
        if existing is not None:
            raise _duplicate(existing, "same_url")

    def _judge(self, request: SubmitItemRequest, identity: Identity) -> SubmissionCheck:
        settings = self._settings
        shortlist = search_repo.shortlist(
            self._session,
            request.title,
            self._clock() - timedelta(days=settings.jev_shortlist_days),
            settings.jev_shortlist_size,
        )
        submission = Submission(
            title=request.title,
            summary=request.summary,
            source_name=request.source_name,
            username=identity.account.username if identity.account else None,
            label=request.label,
            domain=display_domain(request.url),
        )
        check = SubmissionCheck(
            account_id=identity.account.id if identity.account else None,
            ip_hash=identity.ip_hash,
            title=request.title,
            url=request.url,
            created_at=self._clock(),
        )
        try:
            verdict = judge(self._jev, submission, shortlist)
        except JevUnavailableError as error:
            check.outcome = CheckOutcome.UNAVAILABLE
            self._save_rejection(check)
            raise AppError(
                ErrorCode.JEV_UNAVAILABLE,
                "The moderation check is unavailable. Try again later.",
                retry_after=settings.jev_retry_after_seconds,
            ) from error
        _record(check, verdict)
        self._reject_by_verdict(check, verdict)
        return check

    def _reject_by_verdict(self, check: SubmissionCheck, verdict: Verdict) -> None:
        settings = self._settings
        if verdict.harm_probability >= settings.jev_harmful_min:
            check.outcome = CheckOutcome.HARMFUL
            self._save_rejection(check)
            raise AppError(ErrorCode.HARMFUL_CONTENT, "The submission contains harmful language.")
        if (
            verdict.duplicate_of_id is not None
            and verdict.duplicate_probability >= settings.jev_same_story_min
        ):
            check.outcome = CheckOutcome.DUPLICATE
            self._save_rejection(check)
            raise _duplicate(
                item_repo.get_visible(self._session, verdict.duplicate_of_id), "same_story"
            )

    def _save_rejection(self, check: SubmissionCheck) -> None:
        self._session.add(check)
        self._session.commit()

    def _insert(
        self,
        request: SubmitItemRequest,
        identity: Identity,
        check: SubmissionCheck,
    ) -> ItemDetail:
        item = Item(
            title=request.title,
            url=request.url,
            account_id=identity.account.id if identity.account else None,
            label=request.label,
            ip_hash=identity.ip_hash,
            source_name=request.source_name,
            published_at=request.published_at,
            summary=request.summary,
            primary_ref=request.primary_ref,
            links=_links(request),
            created_at=self._clock(),
        )
        check.outcome = CheckOutcome.PUBLISHED
        self._session.add_all([item, check])
        try:
            self._session.flush()
        except IntegrityError as error:
            self._session.rollback()
            existing = item_repo.get_by_url(self._session, request.url)
            if existing is None:
                raise
            raise _duplicate(existing, "same_url") from error
        check.item_id = item.id
        self._session.commit()
        created = item_repo.get_visible(self._session, item.id)
        assert created is not None
        return to_detail(self._session, created, voted=False)


def _links(request: SubmitItemRequest) -> list[ItemLink]:
    corroborating = dict.fromkeys(request.corroborating_urls)
    related = dict.fromkeys(request.related_urls)
    related.pop(request.url, None)
    return [ItemLink(kind=LinkKind.CORROBORATING, url=url) for url in corroborating] + [
        ItemLink(kind=LinkKind.RELATED, url=url) for url in related
    ]


def _record(check: SubmissionCheck, verdict: Verdict) -> None:
    check.model = verdict.model
    check.harm_probability = verdict.harm_probability
    check.duplicate_of_id = verdict.duplicate_of_id
    check.duplicate_probability = verdict.duplicate_probability


def _duplicate(existing: Item | None, reason: str) -> AppError:
    visible = existing if existing is not None and existing.deleted_at is None else None
    return AppError(
        ErrorCode.DUPLICATE,
        "This story is already on the site.",
        {
            "item_id": visible.id if visible else None,
            "title": visible.title if visible else None,
            "url": visible.url if visible else None,
            "reason": reason,
        },
    )
