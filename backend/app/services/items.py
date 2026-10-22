from sqlalchemy.orm import Session

from app.db.repositories import items as item_repo
from app.db.repositories import votes as vote_repo
from app.dto.items import ItemDetail
from app.errors import AppError, ErrorCode
from app.services.item_views import to_detail


class ItemService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, item_id: int, ip_hash: str) -> ItemDetail:
        item = item_repo.get_visible(self._session, item_id)
        if item is None:
            raise AppError(ErrorCode.NOT_FOUND, "Item not found.")
        voted = vote_repo.get(self._session, item_id, ip_hash) is not None
        return to_detail(self._session, item, voted)
