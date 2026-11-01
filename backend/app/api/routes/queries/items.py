from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import FeedServiceDep, ItemServiceDep, RequestCredentials
from app.dto.items import FeedQuery, FeedResponse, ItemDetail

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
def list_items(
    query: Annotated[FeedQuery, Query()],
    credentials: RequestCredentials,
    feed: FeedServiceDep,
) -> FeedResponse:
    return feed.get_feed(query, credentials.ip_hash)


@router.get("/{item_id}")
def get_item(item_id: int, credentials: RequestCredentials, items: ItemServiceDep) -> ItemDetail:
    return items.get(item_id, credentials.ip_hash)
