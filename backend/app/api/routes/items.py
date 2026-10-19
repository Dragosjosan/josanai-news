from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.api.dependencies import (
    AppSettings,
    FeedServiceDep,
    PublishingServiceDep,
    RequestCredentials,
)
from app.dto.items import FeedQuery, FeedResponse, ItemDetail, SubmitItemRequest

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
def list_items(query: Annotated[FeedQuery, Query()], feed: FeedServiceDep) -> FeedResponse:
    return feed.get_front_page(query)


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
