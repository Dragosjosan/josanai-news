from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import make_url

BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env", env_prefix="NEWS_", extra="ignore"
    )

    app_name: str = "news-api"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///data/news.db"
    max_body_bytes: int = Field(default=64 * 1024, gt=0)

    feed_size: int = Field(default=70, gt=0)
    rank_candidates: int = Field(default=500, gt=0)
    rank_gravity: float = Field(default=1.0, gt=0)
    rank_click_w: float = Field(default=0.0, ge=0)
    rank_downvote_p: float = Field(default=0.8, gt=0, le=1)

    @field_validator("database_url", mode="after")
    @classmethod
    def resolve_sqlite_path(cls, value: str) -> str:
        url = make_url(value)
        if url.get_backend_name() == "sqlite" and url.database not in (None, "", ":memory:"):
            path = Path(url.database)
            if not path.is_absolute():
                url = url.set(database=str(BACKEND_ROOT / path))
        return url.render_as_string(hide_password=False)


settings = Settings()
