from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Account, AccountKind, AccountSession


def get_agent_by_key_hash(session: Session, key_hash: str) -> Account | None:
    statement = select(Account).where(
        Account.api_key_hash == key_hash, Account.kind == AccountKind.AGENT
    )
    return session.scalar(statement)


def get_by_session_hash(session: Session, token_hash: str, now: datetime) -> Account | None:
    statement = (
        select(Account)
        .join(AccountSession, AccountSession.account_id == Account.id)
        .where(AccountSession.token_hash == token_hash, AccountSession.expires_at > now)
    )
    return session.scalar(statement)
