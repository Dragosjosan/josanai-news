from fastapi import APIRouter, Response, status

from app.api.dependencies import (
    CommentServiceDep,
    CommentWriterCredentials,
    RequestCredentials,
)
from app.dto.comments import CommentResponse, SubmitCommentRequest, ThreadResponse

router = APIRouter(tags=["comments"])


@router.get("/items/{item_id}/comments")
def list_comments(
    item_id: int, credentials: RequestCredentials, comments: CommentServiceDep
) -> ThreadResponse:
    return comments.thread(item_id, credentials)


@router.post("/items/{item_id}/comments", status_code=status.HTTP_201_CREATED)
def submit_comment(
    item_id: int,
    body: SubmitCommentRequest,
    credentials: CommentWriterCredentials,
    comments: CommentServiceDep,
) -> CommentResponse:
    return comments.submit(item_id, body, credentials)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int, credentials: RequestCredentials, comments: CommentServiceDep
) -> Response:
    comments.delete(comment_id, credentials)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
