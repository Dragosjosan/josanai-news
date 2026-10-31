from collections.abc import Callable
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Account, Comment, Item, Role, utc_now
from app.db.repositories import accounts as account_repo
from app.db.repositories import comments as comment_repo
from app.db.repositories import items as item_repo
from app.db.repositories import reports as report_repo
from app.db.repositories import sessions as session_repo
from app.dto.accounts import AccountResponse
from app.dto.reports import (
    BulkDeleteRequest,
    BulkDeleteResponse,
    ReportedComment,
    ReportListResponse,
    ReviewReport,
)
from app.errors import AppError, ErrorCode
from app.services.auth import to_response
from app.services.item_views import to_summary


class AdminService:
    def __init__(self, session: Session, clock: Callable[[], datetime] = utc_now) -> None:
        self._session = session
        self._clock = clock

    def reports(self) -> ReportListResponse:
        rows = report_repo.list_open(self._session)
        item_ids = list({row.item_id for row in rows})
        items = {item.id: item for item in item_repo.get_items_in_order(self._session, item_ids)}
        counts = comment_repo.visible_counts(self._session, item_ids)
        comments = comment_repo.get_many(
            self._session, [row.comment_id for row in rows if row.comment_id is not None]
        )
        return ReportListResponse(
            reports=[
                ReviewReport(
                    id=row.id,
                    item=to_summary(items[row.item_id], False, counts.get(row.item_id, 0)),
                    comment=_reported_comment(comments[row.comment_id])
                    if row.comment_id is not None
                    else None,
                    harm_probability=row.harm_probability,
                    created_at=row.created_at,
                )
                for row in rows
            ]
        )

    def hide_report(self, report_id: int) -> None:
        report = report_repo.get(self._session, report_id)
        if report is None:
            raise AppError(ErrorCode.NOT_FOUND, "Report not found.")
        if report.hidden_at is None:
            report.hidden_at = self._clock()
            self._session.commit()

    def delete_item(self, item_id: int) -> None:
        item = self._require_item(item_id)
        if item.deleted_at is None:
            item.deleted_at = self._clock()
            self._session.commit()

    def bulk_delete(self, request: BulkDeleteRequest) -> BulkDeleteResponse:
        items = self._submitter_items(self._require_item(request.item_id))
        if not request.dry_run:
            now = self._clock()
            for item in items:
                item.deleted_at = now
            self._session.commit()
        return BulkDeleteResponse(deleted=len(items))

    def make_admin(self, username: str) -> AccountResponse:
        account = self._require_account(username)
        account.role = Role.ADMIN
        self._session.commit()
        return to_response(account)

    def anonymize_account(self, username: str) -> None:
        account = self._require_account(username)
        if account.role is Role.ADMIN:
            raise AppError(
                ErrorCode.FORBIDDEN, "Remove the admin role on the server before deleting this."
            )
        account.username = f"deleted-{account.id}"
        account.password_hash = None
        account.api_key_hash = None
        session_repo.delete_for_account(self._session, account.id)
        self._session.commit()

    def _submitter_items(self, item: Item) -> list[Item]:
        if item.account_id is not None:
            return item_repo.visible_by_account(self._session, item.account_id)
        if item.ip_hash is not None:
            return item_repo.visible_by_ip_hash(self._session, item.ip_hash)
        return []

    def _require_item(self, item_id: int) -> Item:
        item = item_repo.get(self._session, item_id)
        if item is None:
            raise AppError(ErrorCode.NOT_FOUND, "Item not found.")
        return item

    def _require_account(self, username: str) -> Account:
        account = account_repo.get_by_username(self._session, username.lower())
        if account is None:
            raise AppError(ErrorCode.NOT_FOUND, "Account not found.")
        return account


def _reported_comment(comment: Comment) -> ReportedComment:
    return ReportedComment(
        id=comment.id,
        author=comment.account.username if comment.account is not None else None,
        text=comment.text,
    )
