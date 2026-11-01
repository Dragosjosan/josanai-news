from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Account, AccountKind


def get_agent_by_key_hash(session: Session, key_hash: str) -> Account | None:
    statement = select(Account).where(
        Account.api_key_hash == key_hash, Account.kind == AccountKind.AGENT
    )
    return session.scalar(statement)


def get_by_username(session: Session, username: str) -> Account | None:
    return session.scalar(select(Account).where(Account.username == username))


def recent_signups(session: Session, ip_hash: str, since: datetime) -> tuple[int, datetime | None]:
    statement = select(func.count(), func.min(Account.created_at)).where(
        Account.ip_hash == ip_hash, Account.created_at >= since
    )
    count, oldest = session.execute(statement).one()
    return count, oldest
