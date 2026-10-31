from datetime import datetime

from sqlalchemy.orm import Session

from app.config import Settings
from app.db.models import Report


def file_report(
    session: Session,
    settings: Settings,
    item_id: int,
    comment_id: int | None,
    harm_probability: float | None,
    now: datetime,
) -> None:
    if harm_probability is None or harm_probability >= settings.jev_report_min:
        session.add(
            Report(
                item_id=item_id,
                comment_id=comment_id,
                harm_probability=harm_probability,
                created_at=now,
            )
        )
