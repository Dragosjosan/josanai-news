from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import Account, UserSession


def get_account(session: Session, token_hash: str, since: datetime) -> Account | None:
    statement = (
        select(Account)
        .join(UserSession, UserSession.account_id == Account.id)
        .where(UserSession.token_hash == token_hash, UserSession.created_at >= since)
    )
    return session.scalar(statement)


def delete_one(session: Session, token_hash: str) -> None:
    session.execute(delete(UserSession).where(UserSession.token_hash == token_hash))


def delete_for_account(session: Session, account_id: int) -> None:
    session.execute(delete(UserSession).where(UserSession.account_id == account_id))
