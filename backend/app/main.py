from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.middleware.body_limit import BodyLimitMiddleware
from app.api.middleware.json_only import JsonOnlyMiddleware
from app.api.router import api_router
from app.api.routes import auth, health
from app.clients.jev import JevClient
from app.config import Settings, settings
from app.db.connection import build_engine, build_session_factory, prepare_database_directory


def create_app(app_settings: Settings | None = None) -> FastAPI:
    config = app_settings or settings
    engine = build_engine(config.database_url)
    jev = JevClient(
        api_key=config.jev_api_key.get_secret_value() if config.jev_api_key else None,
        base_url=config.jev_base_url,
        model=config.jev_model,
        timeout_seconds=config.jev_timeout_seconds,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        prepare_database_directory(config.database_url)
        try:
            yield
        finally:
            jev.close()
            engine.dispose()

    app = FastAPI(title=config.app_name, lifespan=lifespan)
    app.state.settings = config
    app.state.session_factory = build_session_factory(engine)
    app.state.jev = jev
    register_error_handlers(app)
    app.add_middleware(JsonOnlyMiddleware)
    app.add_middleware(BodyLimitMiddleware, max_bytes=config.max_body_bytes)
    app.include_router(health.router)
    app.include_router(api_router, prefix=config.api_prefix)
    if config.accounts_enabled:
        app.include_router(auth.signup_router, prefix=config.api_prefix)
    return app


app = create_app()
