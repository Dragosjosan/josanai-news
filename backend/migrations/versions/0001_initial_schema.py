from collections.abc import Sequence
from datetime import UTC, datetime

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
        sa.Column("username_key", sa.String(length=32), nullable=False),
        sa.Column(
            "kind",
            sa.Enum("human", "agent", "admin", name="accountkind", native_enum=False, length=16),
            nullable=False,
        ),
        sa.Column("publisher_name", sa.String(length=40), nullable=True),
        sa.Column("publisher_key", sa.String(length=40), nullable=True),
        sa.Column("api_key_hash", sa.String(length=64), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.Column("deleted_at", sa.String(length=24), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_accounts")),
        sa.UniqueConstraint("api_key_hash", name=op.f("uq_accounts_api_key_hash")),
        sa.UniqueConstraint("publisher_key", name=op.f("uq_accounts_publisher_key")),
        sa.UniqueConstraint("username", name=op.f("uq_accounts_username")),
        sa.UniqueConstraint("username_key", name=op.f("uq_accounts_username_key")),
    )
    op.create_table(
        "rate_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "action",
            sa.Enum(
                "submit",
                "vote",
                "click",
                "comment",
                "flag",
                "signup",
                "login",
                name="rateaction",
                native_enum=False,
                length=16,
            ),
            nullable=False,
        ),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rate_events")),
    )
    with op.batch_alter_table("rate_events", schema=None) as batch_op:
        batch_op.create_index(
            "ix_rate_events_action_key_created_at", ["action", "key", "created_at"], unique=False
        )

    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_topics")),
        sa.UniqueConstraint("slug", name=op.f("uq_topics_slug")),
    )
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("canonical_url", sa.String(length=2048), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("publisher", sa.String(length=40), nullable=True),
        sa.Column("publisher_key", sa.String(length=40), nullable=True),
        sa.Column("submitter_ip_hash", sa.String(length=64), nullable=True),
        sa.Column("source_name", sa.String(length=200), nullable=True),
        sa.Column("published_at", sa.String(length=24), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("primary_ref", sa.String(length=200), nullable=True),
        sa.Column("provenance_score", sa.Float(), nullable=True),
        sa.Column("upvotes", sa.Integer(), nullable=False),
        sa.Column("downvotes", sa.Integer(), nullable=False),
        sa.Column("unique_clicks", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.Column("deleted_at", sa.String(length=24), nullable=True),
        sa.Column("deleted_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name=op.f("fk_items_account_id_accounts")
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"], ["accounts.id"], name=op.f("fk_items_deleted_by_id_accounts")
        ),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], name=op.f("fk_items_topic_id_topics")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_items")),
        sa.UniqueConstraint("canonical_url", name=op.f("uq_items_canonical_url")),
    )
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_items_account_id"), ["account_id"], unique=False)
        batch_op.create_index("ix_items_created_at_id", ["created_at", "id"], unique=False)
        batch_op.create_index(batch_op.f("ix_items_publisher_key"), ["publisher_key"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_items_submitter_ip_hash"), ["submitter_ip_hash"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_items_topic_id"), ["topic_id"], unique=False)

    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.Column("expires_at", sa.String(length=24), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name=op.f("fk_sessions_account_id_accounts")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_sessions_token_hash")),
    )
    with op.batch_alter_table("sessions", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_sessions_account_id"), ["account_id"], unique=False)

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
        "click_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("voter_id", sa.String(length=32), nullable=False),
        sa.Column("ip_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_click_events_item_id_items")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_click_events")),
    )
    with op.batch_alter_table("click_events", schema=None) as batch_op:
        batch_op.create_index(
            "ix_click_events_item_id_voter_id", ["item_id", "voter_id"], unique=False
        )

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.Column("deleted_at", sa.String(length=24), nullable=True),
        sa.Column("deleted_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name=op.f("fk_comments_account_id_accounts")
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"], ["accounts.id"], name=op.f("fk_comments_deleted_by_id_accounts")
        ),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], name=op.f("fk_comments_item_id_items")),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["comments.id"], name=op.f("fk_comments_parent_id_comments")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_comments")),
    )
    with op.batch_alter_table("comments", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_comments_account_id"), ["account_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_comments_item_id"), ["item_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_comments_parent_id"), ["parent_id"], unique=False)

    op.create_table(
        "flags",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.Column("updated_at", sa.String(length=24), nullable=False),
        sa.Column("resolved_at", sa.String(length=24), nullable=True),
        sa.Column(
            "resolution",
            sa.Enum("dismissed", "deleted", name="flagresolution", native_enum=False, length=16),
            nullable=True,
        ),
        sa.Column("resolved_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name=op.f("fk_flags_account_id_accounts")
        ),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], name=op.f("fk_flags_item_id_items")),
        sa.ForeignKeyConstraint(
            ["resolved_by_id"], ["accounts.id"], name=op.f("fk_flags_resolved_by_id_accounts")
        ),
        sa.PrimaryKeyConstraint("item_id", "account_id", name=op.f("pk_flags")),
    )
    with op.batch_alter_table("flags", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_flags_account_id"), ["account_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_flags_resolved_at"), ["resolved_at"], unique=False)

    op.create_table(
        "item_corroborating_urls",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_item_corroborating_urls_item_id_items")
        ),
        sa.PrimaryKeyConstraint("item_id", "position", name=op.f("pk_item_corroborating_urls")),
    )
    op.create_table(
        "item_impressions_daily",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("position_bucket", sa.Integer(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_item_impressions_daily_item_id_items")
        ),
        sa.PrimaryKeyConstraint(
            "item_id", "day", "position_bucket", name=op.f("pk_item_impressions_daily")
        ),
    )
    op.create_table(
        "item_related_urls",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("canonical_url", sa.String(length=2048), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column(
            "origin",
            sa.Enum("submitted", "jev", name="relationorigin", native_enum=False, length=16),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_item_related_urls_item_id_items")
        ),
        sa.PrimaryKeyConstraint("item_id", "canonical_url", name=op.f("pk_item_related_urls")),
    )
    with op.batch_alter_table("item_related_urls", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_item_related_urls_canonical_url"), ["canonical_url"], unique=False
        )

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
        "submission_checks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("submitter_ip_hash", sa.String(length=64), nullable=True),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("canonical_url", sa.String(length=2048), nullable=False),
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
        sa.Column(
            "harm_category",
            sa.Enum(
                "none",
                "hate",
                "harassment",
                "violence",
                "sexual",
                "self_harm",
                "scam",
                name="harmcategory",
                native_enum=False,
                length=16,
            ),
            nullable=True,
        ),
        sa.Column("harm_probability", sa.Float(), nullable=True),
        sa.Column("on_topic_probability", sa.Float(), nullable=True),
        sa.Column(
            "relation",
            sa.Enum(
                "same", "update", "different", name="storyrelation", native_enum=False, length=16
            ),
            nullable=True,
        ),
        sa.Column("relation_probability", sa.Float(), nullable=True),
        sa.Column("matched_item_id", sa.Integer(), nullable=True),
        sa.Column("shortlist_size", sa.Integer(), nullable=False),
        sa.Column("model", sa.String(length=32), nullable=True),
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name=op.f("fk_submission_checks_account_id_accounts")
        ),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_submission_checks_item_id_items")
        ),
        sa.ForeignKeyConstraint(
            ["matched_item_id"],
            ["items.id"],
            name=op.f("fk_submission_checks_matched_item_id_items"),
        ),
        sa.ForeignKeyConstraint(
            ["topic_id"], ["topics.id"], name=op.f("fk_submission_checks_topic_id_topics")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_submission_checks")),
    )
    with op.batch_alter_table("submission_checks", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_submission_checks_account_id"), ["account_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_submission_checks_created_at"), ["created_at"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_submission_checks_item_id"), ["item_id"], unique=False)

    op.create_table(
        "vote_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("voter_id", sa.String(length=32), nullable=False),
        sa.Column("ip_hash", sa.String(length=64), nullable=False),
        sa.Column("direction", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.CheckConstraint("direction IN (-1, 0, 1)", name=op.f("ck_vote_events_direction")),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_vote_events_item_id_items")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vote_events")),
    )
    with op.batch_alter_table("vote_events", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_vote_events_item_id"), ["item_id"], unique=False)

    op.create_table(
        "votes",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("voter_id", sa.String(length=32), nullable=False),
        sa.Column("ip_hash", sa.String(length=64), nullable=False),
        sa.Column("direction", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.Column("updated_at", sa.String(length=24), nullable=False),
        sa.CheckConstraint("direction IN (-1, 1)", name=op.f("ck_votes_direction")),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], name=op.f("fk_votes_item_id_items")),
        sa.PrimaryKeyConstraint("item_id", "voter_id", name=op.f("pk_votes")),
    )
    with op.batch_alter_table("votes", schema=None) as batch_op:
        batch_op.create_index("ix_votes_item_id_ip_hash", ["item_id", "ip_hash"], unique=False)

    _insert_launch_topics()
    _insert_anonymous_account()


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
        sa.column("sort_order", sa.Integer),
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
                "sort_order": topic_id,
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


def _insert_anonymous_account() -> None:
    accounts = sa.table(
        "accounts",
        sa.column("username", sa.String),
        sa.column("username_key", sa.String),
        sa.column("kind", sa.String),
        sa.column("created_at", sa.String),
    )
    created_at = datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    op.bulk_insert(
        accounts,
        [
            {
                "username": "anonymous",
                "username_key": "anonymous",
                "kind": "human",
                "created_at": created_at,
            }
        ],
    )


def downgrade() -> None:
    for table in (
        "votes",
        "vote_events",
        "submission_checks",
        "item_tags",
        "item_related_urls",
        "item_impressions_daily",
        "item_corroborating_urls",
        "flags",
        "comments",
        "click_events",
        "topic_tags",
        "sessions",
        "items",
        "topics",
        "rate_events",
        "accounts",
    ):
        op.drop_table(table)
