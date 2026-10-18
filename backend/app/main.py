from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.api.routes import health
from app.config import Settings, settings
from app.db.connection import build_engine, build_session_factory, prepare_database_directory


def create_app(app_settings: Settings | None = None) -> FastAPI:
    config = app_settings or settings
    engine = build_engine(config.database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        prepare_database_directory(config.database_url)
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(title=config.app_name, lifespan=lifespan)
    app.state.settings = config
    app.state.session_factory = build_session_factory(engine)
    app.include_router(health.router)
    app.include_router(api_router, prefix=config.api_prefix)
    return app


app = create_app()
