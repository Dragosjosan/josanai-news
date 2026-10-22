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
        "topics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_topics")),
        sa.UniqueConstraint("slug", name=op.f("uq_topics_slug")),
    )
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], name=op.f("fk_items_topic_id_topics")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_items")),
        sa.UniqueConstraint("url", name=op.f("uq_items_url")),
    )
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.create_index("ix_items_created_at_id", ["created_at", "id"], unique=False)
        batch_op.create_index(batch_op.f("ix_items_topic_id"), ["topic_id"], unique=False)

    op.create_table(
        "topic_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=48), nullable=False),
        sa.ForeignKeyConstraint(
            ["topic_id"], ["topics.id"], name=op.f("fk_topic_tags_topic_id_topics")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_topic_tags")),
        sa.UniqueConstraint("topic_id", "name", name="uq_topic_tags_topic_id_name"),
    )
    with op.batch_alter_table("topic_tags", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_topic_tags_topic_id"), ["topic_id"], unique=False)

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
        "item_tags",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], name=op.f("fk_item_tags_item_id_items")),
        sa.ForeignKeyConstraint(
            ["tag_id"], ["topic_tags.id"], name=op.f("fk_item_tags_tag_id_topic_tags")
        ),
        sa.PrimaryKeyConstraint("item_id", "tag_id", name=op.f("pk_item_tags")),
    )
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
        batch_op.create_index("ix_votes_ip_hash_created_at", ["ip_hash", "created_at"], unique=False)
    op.create_table(
        "submission_checks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("ip_hash", sa.String(length=64), nullable=True),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column(
            "outcome",
            sa.Enum(
                "published",
                "harmful",
                "off_topic",
                "duplicate",
                "unavailable",
                name="checkoutcome",
                native_enum=False,
                length=16,
            ),
            nullable=False,
        ),
        sa.Column("harm_probability", sa.Float(), nullable=True),
        sa.Column("on_topic_probability", sa.Float(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["topic_id"], ["topics.id"], name=op.f("fk_submission_checks_topic_id_topics")
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

    _create_search_index()
    _insert_launch_topics()


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


LAUNCH_TOPICS = (
    (
        "ai",
        "AI",
        (
            "News about artificial intelligence: model and research releases, agents, "
            "developer tooling, inference, evaluation, and AI policy and regulation."
        ),
        (
            "agents",
            "api",
            "evals",
            "german",
            "inference",
            "latestnews",
            "microsoft",
            "models",
            "policy",
            "python",
            "research",
            "testing",
            "tooling",
        ),
    ),
    (
        "hemophilia",
        "Hemophilia",
        (
            "News about hemophilia A and B and their treatment: clinical trials, regulatory "
            "decisions, gene therapy, factor and non-factor therapies, guidelines, and care."
        ),
        (
            "digital-health",
            "emicizumab",
            "factor-viii",
            "gene-therapy",
            "guidelines",
            "hemophilia-b",
            "inhibitors",
            "pediatrics",
            "pharmacokinetics",
            "prophylaxis",
            "real-world-evidence",
            "regulatory",
            "surgery",
        ),
    ),
)


def _insert_launch_topics() -> None:
    topics = sa.table(
        "topics",
        sa.column("id", sa.Integer),
        sa.column("slug", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
    )
    topic_tags = sa.table(
        "topic_tags",
        sa.column("topic_id", sa.Integer),
        sa.column("name", sa.String),
    )
    op.bulk_insert(
        topics,
        [
            {
                "id": topic_id,
                "slug": slug,
                "name": name,
                "description": description,
            }
            for topic_id, (slug, name, description, _) in enumerate(LAUNCH_TOPICS, start=1)
        ],
    )
    op.bulk_insert(
        topic_tags,
        [
            {"topic_id": topic_id, "name": tag}
            for topic_id, (_, _, _, tags) in enumerate(LAUNCH_TOPICS, start=1)
            for tag in tags
        ],
    )


def downgrade() -> None:
    for trigger in ("items_fts_update", "items_fts_delete", "items_fts_insert"):
        op.execute(f"DROP TRIGGER IF EXISTS {trigger}")
    op.execute("DROP TABLE IF EXISTS items_fts")
    for table in (
        "submission_checks",
        "votes",
        "item_tags",
        "item_links",
        "topic_tags",
        "items",
        "topics",
        "accounts",
    ):
        op.drop_table(table)
