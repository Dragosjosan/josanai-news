import re
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import ColumnClause, column, func, literal_column, select, table
from sqlalchemy.orm import Session

from app.db.models import Item

MAX_QUERY_WORDS = 16
_WORD = re.compile(r"\w+")

_ITEMS_FTS = table("items_fts", column("rowid"))
_FTS: ColumnClause[str] = literal_column("items_fts")


@dataclass(frozen=True, slots=True)
class ShortlistEntry:
    id: int
    title: str
    summary: str | None


def match_query(text_value: str) -> str | None:
    words = list(dict.fromkeys(word.lower() for word in _WORD.findall(text_value)))
    if not words:
        return None
    return " OR ".join(f'"{word}"' for word in words[:MAX_QUERY_WORDS])


def shortlist(
    session: Session, text_value: str, since: datetime, limit: int
) -> list[ShortlistEntry]:
    query = match_query(text_value)
    if query is None:
        return []
    statement = (
        select(Item.id, Item.title, Item.summary)
        .join(_ITEMS_FTS, _ITEMS_FTS.c.rowid == Item.id)
        .where(_FTS.op("MATCH")(query), Item.deleted_at.is_(None), Item.created_at >= since)
        .order_by(func.bm25(_FTS))
        .limit(limit)
    )
    return [ShortlistEntry(*row) for row in session.execute(statement)]
