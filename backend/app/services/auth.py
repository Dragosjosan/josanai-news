from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Account, AccountKind, Role, UserSession
from app.db.repositories import accounts as account_repo
from app.db.repositories import sessions as session_repo
from app.dto.accounts import AccountResponse, LoginRequest, SignupRequest
from app.errors import AppError, ErrorCode
from app.services.identity import (
    Credentials,
    hash_password,
    hash_secret,
    new_secret,
    resolve_identity,
    verify_password,
)


@dataclass(frozen=True, slots=True)
class SignupResult:
    account: AccountResponse
    session_token: str | None
    api_key: str | None


@dataclass(frozen=True, slots=True)
class LoginResult:
    account: AccountResponse
    session_token: str


def to_response(account: Account) -> AccountResponse:
    return AccountResponse(
        id=account.id,
        username=account.username,
        kind=account.kind.value,
        role=account.role.value,
        created_at=account.created_at,
    )


def create_account(
    session: Session,
    kind: AccountKind,
    username: str,
    password: str | None,
    role: Role = Role.USER,
) -> tuple[Account, str | None]:
    api_key = new_secret() if kind is AccountKind.AGENT else None
    account = Account(
        username=username.lower(),
        kind=kind,
        role=role,
        password_hash=hash_password(password) if password is not None else None,
        api_key_hash=hash_secret(api_key) if api_key is not None else None,
    )
    session.add(account)
    try:
        session.flush()
    except IntegrityError as error:
        session.rollback()
        raise AppError(ErrorCode.USERNAME_TAKEN, "That username is taken.") from error
    return account, api_key


def issue_api_key(account: Account) -> str:
    api_key = new_secret()
    account.api_key_hash = hash_secret(api_key)
    return api_key


def set_password(session: Session, account: Account, password: str) -> None:
    account.password_hash = hash_password(password)
    session_repo.delete_for_account(session, account.id)


class AuthService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def signup(self, request: SignupRequest) -> SignupResult:
        if account_repo.get_by_username(self._session, request.username.lower()) is not None:
            raise AppError(ErrorCode.USERNAME_TAKEN, "That username is taken.")
        account, api_key = create_account(
            self._session,
            AccountKind(request.kind),
            request.username,
            request.password,
        )
        token = self._start_session(account) if account.kind is AccountKind.USER else None
        self._session.commit()
        return SignupResult(to_response(account), token, api_key)

    def login(self, request: LoginRequest) -> LoginResult:
        account = account_repo.get_by_username(self._session, request.username.strip().lower())
        if (
            account is None
            or account.kind is not AccountKind.USER
            or account.password_hash is None
            or not verify_password(account.password_hash, request.password)
        ):
            raise AppError(ErrorCode.INVALID_CREDENTIALS, "Wrong username or password.")
        token = self._start_session(account)
        self._session.commit()
        return LoginResult(to_response(account), token)

    def logout(self, session_token: str | None) -> None:
        if session_token is None:
            return
        session_repo.delete_one(self._session, hash_secret(session_token))
        self._session.commit()

    def current(self, credentials: Credentials) -> AccountResponse | None:
        account = resolve_identity(self._session, credentials).account
        return to_response(account) if account is not None else None

    def rotate_key(self, credentials: Credentials) -> str:
        account = resolve_identity(self._session, credentials).account
        if account is None:
            raise AppError(ErrorCode.NOT_AUTHENTICATED, "Send your X-API-Key header.")
        if account.kind is not AccountKind.AGENT:
            raise AppError(ErrorCode.FORBIDDEN, "Only agent accounts have an API key.")
        api_key = issue_api_key(account)
        self._session.commit()
        return api_key

    def _start_session(self, account: Account) -> str:
        token = new_secret()
        self._session.add(UserSession(token_hash=hash_secret(token), account_id=account.id))
        return token
