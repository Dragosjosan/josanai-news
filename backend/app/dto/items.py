from datetime import datetime

from pydantic import BaseModel


class FeedQuery(BaseModel):
    topic: str | None = None
    tag: str | None = None


class ItemResponse(BaseModel):
    id: int
    title: str
    url: str
    domain: str
    topic: str
    tags: list[str]
    score: int
    comment_count: int
    submitted_by: str | None
    created_at: datetime


class FeedResponse(BaseModel):
    items: list[ItemResponse]
