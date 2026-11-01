from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import CommentServiceDep, RequestCredentials
from app.dto.comments import AccountCommentsQuery, ThreadResponse

router = APIRouter(tags=["comments"])


@router.get("/items/{item_id}/comments")
def list_comments(
    item_id: int, credentials: RequestCredentials, comments: CommentServiceDep
) -> ThreadResponse:
    return comments.thread(item_id, credentials)


@router.get("/comments")
def list_account_comments(
    query: Annotated[AccountCommentsQuery, Query()],
    credentials: RequestCredentials,
    comments: CommentServiceDep,
) -> ThreadResponse:
    return comments.by_account(query, credentials)
