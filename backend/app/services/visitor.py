import hashlib
import hmac
import re
from datetime import datetime, timedelta

from app.services.identity import hash_secret, new_secret

VOTER_COOKIE = "voter"
VOTER_LIFETIME = timedelta(days=365)
_ID = re.compile(r"[A-Za-z0-9_-]{43}")


def new_voter(secret: str, now: datetime) -> tuple[str, str]:
    visitor = new_secret()
    payload = f"{visitor}.{int(now.timestamp())}"
    return f"{payload}.{_signature(payload, secret)}", hash_secret(visitor)


def read_voter(token: str | None, secret: str, now: datetime) -> str | None:
    if token is None or len(token) > 160:
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    visitor, issued_at, signature = parts
    if not _ID.fullmatch(visitor) or not issued_at.isascii() or not issued_at.isdigit():
        return None
    if not re.fullmatch(r"[a-f0-9]{64}", signature):
        return None
    if not hmac.compare_digest(_signature(f"{visitor}.{issued_at}", secret), signature):
        return None
    age = now.timestamp() - int(issued_at)
    if not 0 <= age <= VOTER_LIFETIME.total_seconds():
        return None
    return hash_secret(visitor)


def _signature(payload: str, secret: str) -> str:
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
