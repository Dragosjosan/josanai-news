import hashlib
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Account
from app.db.repositories import accounts as account_repo
from app.errors import AppError, ErrorCode


@dataclass(frozen=True, slots=True)
class Credentials:
    api_key: str | None
    session_token: str | None
    ip_hash: str


@dataclass(frozen=True, slots=True)
class Identity:
    account: Account | None
    ip_hash: str


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def hash_ip(ip: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{ip}".encode()).hexdigest()


def resolve_identity(session: Session, credentials: Credentials, now: datetime) -> Identity:
    if credentials.api_key is not None:
        agent = account_repo.get_agent_by_key_hash(session, hash_secret(credentials.api_key))
        if agent is None:
            raise AppError(ErrorCode.INVALID_API_KEY, "The API key is not valid.")
        return Identity(agent, credentials.ip_hash)
    if credentials.session_token:
        account = account_repo.get_by_session_hash(
            session, hash_secret(credentials.session_token), now
        )
        return Identity(account, credentials.ip_hash)
    return Identity(None, credentials.ip_hash)
