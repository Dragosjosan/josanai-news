from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.dto.items import ItemSummary
from app.dto.validation import RequestModel


class ReportedComment(BaseModel):
    id: int
    author: str | None
    text: str


class ReviewReport(BaseModel):
    id: int
    item: ItemSummary
    comment: ReportedComment | None
    harm_probability: float | None
    created_at: datetime


class ReportListResponse(BaseModel):
    reports: list[ReviewReport]


class BulkDeleteRequest(RequestModel):
    item_id: int = Field(gt=0)
    by: Literal["submitter", "account"]
    dry_run: bool = False


class BulkDeleteResponse(BaseModel):
    deleted: int
