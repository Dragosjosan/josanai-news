from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import RequestCredentials, SearchServiceDep
from app.dto.items import SearchQuery, SearchResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search_items(
    query: Annotated[SearchQuery, Query()],
    credentials: RequestCredentials,
    search: SearchServiceDep,
) -> SearchResponse:
    return search.search(query, credentials.ip_hash)
