import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

BACKEND = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def migrated_database(tmp_path_factory: pytest.TempPathFactory) -> Path:
    database = tmp_path_factory.mktemp("template") / "news.db"
    config = Config()
    config.set_main_option("script_location", str(BACKEND / "migrations"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database}")
    command.upgrade(config, "head")
    return database


@pytest.fixture
def client(migrated_database: Path, tmp_path: Path) -> Iterator[TestClient]:
    database = tmp_path / "news.db"
    shutil.copy(migrated_database, database)
    settings = Settings(
        _env_file=None,
        database_url=f"sqlite:///{database}",
        jev_api_key=None,
        cookie_secure=False,
    )
    app = create_app(settings)
    with TestClient(
        app, base_url="http://testserver/api/v1/", raise_server_exceptions=False
    ) as test_client:
        yield test_client
