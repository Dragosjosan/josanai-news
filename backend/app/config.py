from pathlib import Path

from pydantic import Field, SecretStr, field_validator
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

    accounts_enabled: bool = False
    post_requires_account: bool = False
    comment_requires_account: bool = False

    ip_hash_salt: SecretStr = SecretStr("dev-salt")
    submit_per_hour: int = Field(default=10, gt=0)
    vote_per_hour: int = Field(default=120, gt=0)

    jev_api_key: SecretStr | None = None
    jev_base_url: str = "https://api.typesafe.ai"
    jev_model: str = "jev-1.13.0"
    jev_timeout_seconds: float = Field(default=10.0, gt=0)
    jev_retry_after_seconds: int = Field(default=30, gt=0)
    jev_harmful_min: float = Field(default=0.8, ge=0, le=1)
    jev_off_topic_min: float = Field(default=0.8, ge=0, le=1)
    jev_same_story_min: float = Field(default=0.85, ge=0, le=1)
    jev_shortlist_size: int = Field(default=10, gt=0)
    jev_shortlist_days: int = Field(default=30, gt=0)

    feed_size: int = Field(default=70, gt=0)
    rank_candidates: int = Field(default=500, gt=0)
    rank_gravity: float = Field(default=1.0, gt=0)

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
