from collections.abc import Iterator
from dataclasses import replace
from typing import Annotated, cast

from fastapi import Depends, Request, Response
from sqlalchemy.orm import Session

from app.clients.jev import JevClient
from app.config import Settings
from app.db.connection import SessionFactory
from app.db.models import Role, utc_now
from app.errors import AppError, ErrorCode
from app.services.admin import AdminService
from app.services.auth import AuthService
from app.services.comments import CommentService
from app.services.feed import FeedService
from app.services.identity import Credentials, Identity, hash_ip, resolve_identity
from app.services.items import ItemService
from app.services.publishing import PublishingService
from app.services.search import SearchService
from app.services.visitor import VOTER_COOKIE, VOTER_LIFETIME, new_voter, read_voter
from app.services.voting import VotingService

API_KEY_HEADER = "X-API-Key"
SESSION_COOKIE = "session"


def get_session(request: Request) -> Iterator[Session]:
    session_factory = cast(SessionFactory, request.app.state.session_factory)
    with session_factory() as session:
        yield session


def get_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


DatabaseSession = Annotated[Session, Depends(get_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_credentials(request: Request, settings: AppSettings) -> Credentials:
    client_ip = request.client.host if request.client else "unknown"
    return Credentials(
        api_key=request.headers.get(API_KEY_HEADER),
        session_token=request.cookies.get(SESSION_COOKIE),
        ip_hash=hash_ip(client_ip, settings.ip_hash_salt.get_secret_value()),
        voter_id=read_voter(
            request.cookies.get(VOTER_COOKIE), settings.cookie_secret.get_secret_value(), utc_now()
        ),
    )


def get_feed_service(session: DatabaseSession, settings: AppSettings) -> FeedService:
    return FeedService(session, settings)


def get_item_service(session: DatabaseSession) -> ItemService:
    return ItemService(session)


def get_voting_service(session: DatabaseSession, settings: AppSettings) -> VotingService:
    return VotingService(session, settings)


def get_search_service(session: DatabaseSession, settings: AppSettings) -> SearchService:
    return SearchService(session, settings)


def get_auth_service(session: DatabaseSession) -> AuthService:
    return AuthService(session)


def get_admin_service(session: DatabaseSession) -> AdminService:
    return AdminService(session)


def get_publishing_service(
    request: Request, session: DatabaseSession, settings: AppSettings
) -> PublishingService:
    return PublishingService(
        session,
        settings,
        cast(JevClient, request.app.state.jev),
    )


def get_comment_service(
    request: Request, session: DatabaseSession, settings: AppSettings
) -> CommentService:
    return CommentService(session, settings, cast(JevClient, request.app.state.jev))


RequestCredentials = Annotated[Credentials, Depends(get_credentials)]
FeedServiceDep = Annotated[FeedService, Depends(get_feed_service)]
PublishingServiceDep = Annotated[PublishingService, Depends(get_publishing_service)]
ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]
VotingServiceDep = Annotated[VotingService, Depends(get_voting_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
SearchServiceDep = Annotated[SearchService, Depends(get_search_service)]
CommentServiceDep = Annotated[CommentService, Depends(get_comment_service)]
AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]


def get_comment_credentials(
    response: Response, credentials: RequestCredentials, settings: AppSettings
) -> Credentials:
    if credentials.voter_id is not None:
        return credentials
    token, voter_id = new_voter(settings.cookie_secret.get_secret_value(), utc_now())
    response.set_cookie(
        VOTER_COOKIE,
        token,
        max_age=int(VOTER_LIFETIME.total_seconds()),
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )
    return replace(credentials, voter_id=voter_id)


CommentWriterCredentials = Annotated[Credentials, Depends(get_comment_credentials)]


def get_identity(session: DatabaseSession, credentials: RequestCredentials) -> Identity:
    return resolve_identity(session, credentials)


CurrentIdentity = Annotated[Identity, Depends(get_identity)]


def require_admin(identity: CurrentIdentity) -> None:
    if identity.account is None:
        raise AppError(ErrorCode.NOT_AUTHENTICATED, "Log in or send an X-API-Key header.")
    if identity.account.role is not Role.ADMIN:
        raise AppError(ErrorCode.FORBIDDEN, "Only an admin can do this.")
