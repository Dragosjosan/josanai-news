from datetime import datetime
from typing import Literal

from pydantic import BaseModel

VoteDirection = Literal["up", "down"]


class FeedQuery(BaseModel):
    topic: str | None = None
    tag: str | None = None


class ItemSummary(BaseModel):
    id: int
    title: str
    url: str
    domain: str
    topic: str
    tags: list[str]
    score: int
    comment_count: int
    publisher: str | None
    created_at: datetime
    viewer_vote: VoteDirection | None


class FeedResponse(BaseModel):
    items: list[ItemSummary]
