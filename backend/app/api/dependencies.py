from collections.abc import Iterator
from typing import Annotated, cast

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.clients.jev import JevClient
from app.config import Settings
from app.db.connection import SessionFactory
from app.services.feed import FeedService
from app.services.identity import Credentials, hash_ip
from app.services.publishing import PublishingService
from app.services.topics import TopicService

API_KEY_HEADER = "X-API-Key"


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
        ip_hash=hash_ip(client_ip, settings.ip_hash_salt.get_secret_value()),
    )


def get_feed_service(session: DatabaseSession, settings: AppSettings) -> FeedService:
    return FeedService(session, settings)


def get_topic_service(session: DatabaseSession) -> TopicService:
    return TopicService(session)


def get_publishing_service(
    request: Request, session: DatabaseSession, settings: AppSettings
) -> PublishingService:
    return PublishingService(
        session,
        settings,
        cast(JevClient, request.app.state.jev),
    )


RequestCredentials = Annotated[Credentials, Depends(get_credentials)]
FeedServiceDep = Annotated[FeedService, Depends(get_feed_service)]
TopicServiceDep = Annotated[TopicService, Depends(get_topic_service)]
PublishingServiceDep = Annotated[PublishingService, Depends(get_publishing_service)]
