import re
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.db.models import UtcDateTime

MAX_QUERY_WORDS = 16
_WORD = re.compile(r"\w+")

_SHORTLIST = text(
    """
    SELECT items.id, items.title, items.summary
    FROM items_fts
    JOIN items ON items.id = items_fts.rowid
    WHERE items_fts MATCH :query
      AND items.deleted_at IS NULL
      AND items.created_at >= :since
    ORDER BY bm25(items_fts)
    LIMIT :limit
    """
).bindparams(bindparam("since", type_=UtcDateTime()))


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
    rows = session.execute(_SHORTLIST, {"query": query, "since": since, "limit": limit})
    return [ShortlistEntry(*row) for row in rows]
