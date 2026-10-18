from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import FeedServiceDep
from app.dto.items import FeedQuery, FeedResponse

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
def list_items(query: Annotated[FeedQuery, Query()], feed: FeedServiceDep) -> FeedResponse:
    return feed.get_front_page(query)
