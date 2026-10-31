from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column(
            "kind",
            sa.Enum("user", "agent", name="accountkind", native_enum=False, length=16),
            nullable=False,
        ),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("api_key_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_accounts")),
        sa.UniqueConstraint("api_key_hash", name=op.f("uq_accounts_api_key_hash")),
        sa.UniqueConstraint("username", name=op.f("uq_accounts_username")),
    )
    op.create_table(
        "sessions",
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name=op.f("fk_sessions_account_id_accounts")
        ),
        sa.PrimaryKeyConstraint("token_hash", name=op.f("pk_sessions")),
    )
    with op.batch_alter_table("sessions", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_sessions_account_id"), ["account_id"], unique=False)
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("label", sa.String(length=40), nullable=True),
        sa.Column("ip_hash", sa.String(length=64), nullable=True),
        sa.Column("source_name", sa.String(length=200), nullable=True),
        sa.Column("published_at", sa.String(length=24), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("primary_ref", sa.String(length=200), nullable=True),
        sa.Column("upvotes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.Column("deleted_at", sa.String(length=24), nullable=True),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name=op.f("fk_items_account_id_accounts")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_items")),
        sa.UniqueConstraint("url", name=op.f("uq_items_url")),
    )
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.create_index("ix_items_created_at_id", ["created_at", "id"], unique=False)

    op.create_table(
        "item_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum("corroborating", "related", name="linkkind", native_enum=False, length=16),
            nullable=False,
        ),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_item_links_item_id_items")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_item_links")),
        sa.UniqueConstraint("item_id", "kind", "url", name="uq_item_links_item_id_kind_url"),
    )
    with op.batch_alter_table("item_links", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_item_links_url"), ["url"], unique=False)

    op.create_table(
        "votes",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("ip_hash", sa.String(length=64), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name=op.f("fk_votes_account_id_accounts")
        ),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], name=op.f("fk_votes_item_id_items")),
        sa.PrimaryKeyConstraint("item_id", "ip_hash", name=op.f("pk_votes")),
    )
    with op.batch_alter_table("votes", schema=None) as batch_op:
        batch_op.create_index(
            "ix_votes_ip_hash_created_at", ["ip_hash", "created_at"], unique=False
        )
    op.create_table(
        "submission_checks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("ip_hash", sa.String(length=64), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column(
            "outcome",
            sa.Enum(
                "published",
                "harmful",
                "duplicate",
                "unavailable",
                name="checkoutcome",
                native_enum=False,
                length=16,
            ),
            nullable=False,
        ),
        sa.Column("harm_probability", sa.Float(), nullable=True),
        sa.Column("duplicate_of_id", sa.Integer(), nullable=True),
        sa.Column("duplicate_probability", sa.Float(), nullable=True),
        sa.Column("model", sa.String(length=32), nullable=True),
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name=op.f("fk_submission_checks_account_id_accounts")
        ),
        sa.ForeignKeyConstraint(
            ["duplicate_of_id"],
            ["items.id"],
            name=op.f("fk_submission_checks_duplicate_of_id_items"),
        ),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_submission_checks_item_id_items")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_submission_checks")),
    )
    with op.batch_alter_table("submission_checks", schema=None) as batch_op:
        batch_op.create_index(
            "ix_submission_checks_account_id_created_at", ["account_id", "created_at"], unique=False
        )
        batch_op.create_index(
            "ix_submission_checks_ip_hash_created_at", ["ip_hash", "created_at"], unique=False
        )

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("voter_id", sa.String(length=64), nullable=False),
        sa.Column("ip_hash", sa.String(length=64), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.Column("deleted_at", sa.String(length=24), nullable=True),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], name=op.f("fk_comments_item_id_items")),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["comments.id"], name=op.f("fk_comments_parent_id_comments")
        ),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name=op.f("fk_comments_account_id_accounts")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_comments")),
    )
    with op.batch_alter_table("comments", schema=None) as batch_op:
        batch_op.create_index(
            "ix_comments_item_id_created_at_id", ["item_id", "created_at", "id"], unique=False
        )

    op.create_table(
        "comment_checks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("ip_hash", sa.String(length=64), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column(
            "outcome",
            sa.Enum(
                "published",
                "harmful",
                "unavailable",
                name="commentcheckoutcome",
                native_enum=False,
                length=16,
            ),
            nullable=False,
        ),
        sa.Column("harm_probability", sa.Float(), nullable=True),
        sa.Column("model", sa.String(length=32), nullable=True),
        sa.Column("comment_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_comment_checks_item_id_items")
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["comments.id"], name=op.f("fk_comment_checks_parent_id_comments")
        ),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name=op.f("fk_comment_checks_account_id_accounts")
        ),
        sa.ForeignKeyConstraint(
            ["comment_id"], ["comments.id"], name=op.f("fk_comment_checks_comment_id_comments")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_comment_checks")),
    )
    with op.batch_alter_table("comment_checks", schema=None) as batch_op:
        batch_op.create_index(
            "ix_comment_checks_account_id_created_at", ["account_id", "created_at"], unique=False
        )
        batch_op.create_index(
            "ix_comment_checks_ip_hash_created_at", ["ip_hash", "created_at"], unique=False
        )

    _create_search_index()


SEARCH_INDEX = (
    """
    CREATE VIRTUAL TABLE items_fts USING fts5(
        title, summary, source_name,
        content='items', content_rowid='id',
        tokenize='unicode61 remove_diacritics 2'
    )
    """,
    """
    CREATE TRIGGER items_fts_insert AFTER INSERT ON items BEGIN
        INSERT INTO items_fts(rowid, title, summary, source_name)
        VALUES (new.id, new.title, new.summary, new.source_name);
    END
    """,
    """
    CREATE TRIGGER items_fts_delete AFTER DELETE ON items BEGIN
        INSERT INTO items_fts(items_fts, rowid, title, summary, source_name)
        VALUES ('delete', old.id, old.title, old.summary, old.source_name);
    END
    """,
    """
    CREATE TRIGGER items_fts_update AFTER UPDATE OF title, summary, source_name ON items BEGIN
        INSERT INTO items_fts(items_fts, rowid, title, summary, source_name)
        VALUES ('delete', old.id, old.title, old.summary, old.source_name);
        INSERT INTO items_fts(rowid, title, summary, source_name)
        VALUES (new.id, new.title, new.summary, new.source_name);
    END
    """,
)


def _create_search_index() -> None:
    for statement in SEARCH_INDEX:
        op.execute(statement)


def downgrade() -> None:
    for trigger in ("items_fts_update", "items_fts_delete", "items_fts_insert"):
        op.execute(f"DROP TRIGGER IF EXISTS {trigger}")
    op.execute("DROP TABLE IF EXISTS items_fts")
    for table in (
        "comment_checks",
        "comments",
        "submission_checks",
        "votes",
        "item_links",
        "items",
        "sessions",
        "accounts",
    ):
        op.drop_table(table)
