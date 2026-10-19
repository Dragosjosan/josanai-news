from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import SubmissionCheck


def recent_attempts(
    session: Session, account_id: int | None, ip_hash: str, since: datetime
) -> tuple[int, datetime | None]:
    by_submitter = (
        SubmissionCheck.account_id == account_id
        if account_id is not None
        else SubmissionCheck.ip_hash == ip_hash
    )
    statement = select(func.count(), func.min(SubmissionCheck.created_at)).where(
        by_submitter, SubmissionCheck.created_at >= since
    )
    count, oldest = session.execute(statement).one()
    return count, oldest
