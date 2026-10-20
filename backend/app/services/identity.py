import hashlib
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models import Account
from app.db.repositories import accounts as account_repo
from app.errors import AppError, ErrorCode


@dataclass(frozen=True, slots=True)
class Credentials:
    api_key: str | None
    ip_hash: str


@dataclass(frozen=True, slots=True)
class Identity:
    account: Account | None
    ip_hash: str


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def hash_ip(ip: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{ip}".encode()).hexdigest()


def resolve_identity(session: Session, credentials: Credentials) -> Identity:
    if credentials.api_key is None:
        return Identity(None, credentials.ip_hash)
    agent = account_repo.get_agent_by_key_hash(session, hash_secret(credentials.api_key))
    if agent is None:
        raise AppError(ErrorCode.INVALID_API_KEY, "The API key is not valid.")
    return Identity(agent, credentials.ip_hash)
