from datetime import datetime

from pydantic import BaseModel, Field

from app.dto.validation import CommentText, RequestModel


class SubmitCommentRequest(RequestModel):
    text: CommentText
    parent_id: int | None = Field(default=None, gt=0)


class AccountCommentsQuery(RequestModel):
    username: str = Field(max_length=32)


class CommentResponse(BaseModel):
    id: int
    item_id: int
    parent_id: int | None
    author: str | None
    text: str | None
    created_at: datetime
    deleted: bool
    can_delete: bool


class ThreadResponse(BaseModel):
    comments: list[CommentResponse]
