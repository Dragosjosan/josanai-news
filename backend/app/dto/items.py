from datetime import UTC, date, datetime, timedelta
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    Field,
    field_validator,
)

from app.dto.validation import (
    Label,
    PrimaryRef,
    RequestModel,
    SearchText,
    SourceName,
    Summary,
    Title,
    WebUrl,
)

VoteDirection = Literal["up"]

MAX_FUTURE = timedelta(hours=24)


def _not_far_future(value: datetime) -> datetime:
    if value > datetime.now(UTC) + MAX_FUTURE:
        raise ValueError("must not be more than 24 hours in the future")
    return value


PublishedAt = Annotated[AwareDatetime, AfterValidator(_not_far_future)]


class FeedQuery(BaseModel):
    sort: Literal["top", "new"] = "top"
    day: date | None = None


class SearchQuery(BaseModel):
    q: SearchText = ""
    page: int = Field(default=1, ge=1)


class SubmitItemRequest(RequestModel):
    contract_version: str
    title: Title
    url: WebUrl
    label: Label | None = None
    source_name: SourceName | None = None
    published_at: PublishedAt | None = None
    summary: Summary | None = None
    primary_ref: PrimaryRef | None = None

    @field_validator("summary", mode="before")
    @classmethod
    def empty_summary_is_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class ItemSummary(BaseModel):
    id: int
    title: str
    url: str
    domain: str
    summary: str | None
    score: int
    comment_count: int
    username: str | None
    label: str | None
    created_at: datetime
    viewer_vote: VoteDirection | None


class ItemDetail(ItemSummary):
    source_name: str | None
    published_at: datetime | None
    primary_ref: str | None


class FeedResponse(BaseModel):
    items: list[ItemSummary]


class SearchResponse(BaseModel):
    items: list[ItemSummary]
    page: int
    has_more: bool


class VoteRequest(RequestModel):
    direction: Literal["up", "none"]


class VoteResponse(BaseModel):
    score: int
    viewer_vote: VoteDirection | None
