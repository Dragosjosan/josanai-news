import hashlib
import ipaddress
import secrets
from dataclasses import dataclass
from datetime import timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from sqlalchemy.orm import Session

from app.db.models import Account, utc_now
from app.db.repositories import accounts as account_repo
from app.db.repositories import sessions as session_repo
from app.errors import AppError, ErrorCode

SESSION_LIFETIME = timedelta(days=30)

_password_hasher = PasswordHasher()


@dataclass(frozen=True, slots=True)
class Credentials:
    api_key: str | None
    session_token: str | None
    ip_hash: str
    voter_id: str | None = None


@dataclass(frozen=True, slots=True)
class Identity:
    account: Account | None
    ip_hash: str
    voter_id: str | None = None


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def new_secret() -> str:
    return secrets.token_urlsafe(32)


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except VerificationError:
        return False


def hash_ip(ip: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{_visitor_network(ip)}".encode()).hexdigest()


def _visitor_network(ip: str) -> str:
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return ip
    if isinstance(address, ipaddress.IPv6Address):
        if address.ipv4_mapped is not None:
            return str(address.ipv4_mapped)
        return str(ipaddress.IPv6Network((address, 64), strict=False).network_address)
    return str(address)


def resolve_identity(session: Session, credentials: Credentials) -> Identity:
    if credentials.api_key is not None:
        agent = account_repo.get_agent_by_key_hash(session, hash_secret(credentials.api_key))
        if agent is None:
            raise AppError(ErrorCode.INVALID_API_KEY, "The API key is not valid.")
        return Identity(agent, credentials.ip_hash, credentials.voter_id)
    if credentials.session_token is not None:
        user = session_repo.get_account(
            session, hash_secret(credentials.session_token), utc_now() - SESSION_LIFETIME
        )
        return Identity(user, credentials.ip_hash, credentials.voter_id)
    return Identity(None, credentials.ip_hash, credentials.voter_id)
