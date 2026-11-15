from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SEARCH_TRIGGERS = (
    """
    CREATE TRIGGER IF NOT EXISTS items_fts_insert AFTER INSERT ON items BEGIN
        INSERT INTO items_fts(rowid, title, summary, source_name)
        VALUES (new.id, new.title, new.summary, new.source_name);
    END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS items_fts_delete AFTER DELETE ON items BEGIN
        INSERT INTO items_fts(items_fts, rowid, title, summary, source_name)
        VALUES ('delete', old.id, old.title, old.summary, old.source_name);
    END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS items_fts_update
    AFTER UPDATE OF title, summary, source_name ON items BEGIN
        INSERT INTO items_fts(items_fts, rowid, title, summary, source_name)
        VALUES ('delete', old.id, old.title, old.summary, old.source_name);
        INSERT INTO items_fts(rowid, title, summary, source_name)
        VALUES (new.id, new.title, new.summary, new.source_name);
    END
    """,
)


def upgrade() -> None:
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.drop_constraint("uq_items_url", type_="unique")
        batch_op.create_index(
            "uq_items_url_visible",
            ["url"],
            unique=True,
            sqlite_where=sa.text("deleted_at IS NULL"),
        )
    _restore_search_index()


def downgrade() -> None:
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.drop_index("uq_items_url_visible")
        batch_op.create_unique_constraint("uq_items_url", ["url"])
    _restore_search_index()


def _restore_search_index() -> None:
    for statement in SEARCH_TRIGGERS:
        op.execute(statement)
    op.execute("INSERT INTO items_fts(items_fts) VALUES ('rebuild')")
