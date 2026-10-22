from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    BeforeValidator,
    Field,
    StringConstraints,
)

from app.dto.validation import (
    Label,
    PrimaryRef,
    RequestModel,
    SourceName,
    Summary,
    Title,
    WebUrl,
    clean_line,
)

VoteDirection = Literal["up"]

MAX_FUTURE = timedelta(hours=24)

TagName = Annotated[
    str, BeforeValidator(clean_line), StringConstraints(min_length=1, max_length=48)
]
TopicSlug = Annotated[
    str, BeforeValidator(clean_line), StringConstraints(min_length=1, max_length=32)
]


def _not_far_future(value: datetime) -> datetime:
    if value > datetime.now(UTC) + MAX_FUTURE:
        raise ValueError("must not be more than 24 hours in the future")
    return value


PublishedAt = Annotated[AwareDatetime, AfterValidator(_not_far_future)]


class FeedQuery(BaseModel):
    topic: str | None = None
    tag: str | None = None


class SubmitItemRequest(RequestModel):
    contract_version: str
    title: Title
    url: WebUrl
    topic: TopicSlug
    tags: list[TagName] = Field(default_factory=list, max_length=5)
    label: Label | None = None
    source_name: SourceName | None = None
    published_at: PublishedAt | None = None
    summary: Summary | None = None
    primary_ref: PrimaryRef | None = None
    corroborating_urls: list[WebUrl] = Field(default_factory=list, max_length=10)
    related_urls: list[WebUrl] = Field(default_factory=list, max_length=10)


class ItemSummary(BaseModel):
    id: int
    title: str
    url: str
    domain: str
    topic: str
    tags: list[str]
    score: int
    comment_count: int
    username: str | None
    label: str | None
    created_at: datetime
    viewer_vote: VoteDirection | None


class Link(BaseModel):
    url: str
    domain: str


class ItemRef(BaseModel):
    id: int
    title: str
    domain: str
    created_at: datetime


class ItemDetail(ItemSummary):
    source_name: str | None
    published_at: datetime | None
    summary: str | None
    primary_ref: str | None
    corroborating: list[Link]
    earlier: list[ItemRef]
    later: list[ItemRef]
    viewer_reported: bool


class FeedResponse(BaseModel):
    items: list[ItemSummary]


class VoteRequest(RequestModel):
    direction: Literal["up", "none"]


class VoteResponse(BaseModel):
    score: int
    viewer_vote: VoteDirection | None
