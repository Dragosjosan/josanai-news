from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import (
    AdminServiceDep,
    AppSettings,
    FeedServiceDep,
    ItemServiceDep,
    PublishingServiceDep,
    RequestCredentials,
    VotingServiceDep,
    require_admin,
)
from app.dto.items import (
    FeedQuery,
    FeedResponse,
    ItemDetail,
    SubmitItemRequest,
    VoteRequest,
    VoteResponse,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
def list_items(
    query: Annotated[FeedQuery, Query()],
    credentials: RequestCredentials,
    feed: FeedServiceDep,
) -> FeedResponse:
    return feed.get_feed(query, credentials.ip_hash)


@router.post("", status_code=status.HTTP_201_CREATED)
def submit_item(
    body: SubmitItemRequest,
    response: Response,
    credentials: RequestCredentials,
    publishing: PublishingServiceDep,
    settings: AppSettings,
) -> ItemDetail:
    item = publishing.submit(body, credentials)
    response.headers["Location"] = f"{settings.api_prefix}/items/{item.id}"
    return item


@router.get("/{item_id}")
def get_item(item_id: int, credentials: RequestCredentials, items: ItemServiceDep) -> ItemDetail:
    return items.get(item_id, credentials.ip_hash)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_item(item_id: int, admin: AdminServiceDep) -> Response:
    admin.delete_item(item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{item_id}/vote")
def vote_item(
    item_id: int,
    body: VoteRequest,
    credentials: RequestCredentials,
    voting: VotingServiceDep,
) -> VoteResponse:
    return voting.vote(item_id, body, credentials)
