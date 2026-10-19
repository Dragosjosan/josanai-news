from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TOPIC_DESCRIPTIONS = {
    "ai": (
        "News about artificial intelligence: model and research releases, agents, "
        "developer tooling, inference, evaluation, and AI policy and regulation."
    ),
    "hemophilia": (
        "News about hemophilia A and B and their treatment: clinical trials, regulatory "
        "decisions, gene therapy, factor and non-factor therapies, guidelines, and care."
    ),
}


def _enum(name: str, *values: str) -> sa.Enum:
    return sa.Enum(*values, name=name, native_enum=False, length=16)


def _utc_now_text() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def upgrade() -> None:
    _upgrade_topics()
    _upgrade_accounts()
    _upgrade_items()
    _create_item_links()
    _create_sessions()
    _create_votes_and_clicks()
    _create_flags()
    _create_submission_checks()
    _create_rate_events()


def _upgrade_topics() -> None:
    with op.batch_alter_table("topics", schema=None) as batch_op:
        batch_op.add_column(sa.Column("description", sa.Text(), nullable=False, server_default=""))
    topics = sa.table("topics", sa.column("slug", sa.String), sa.column("description", sa.Text))
    for slug, description in TOPIC_DESCRIPTIONS.items():
        op.execute(topics.update().where(topics.c.slug == slug).values(description=description))


def _upgrade_accounts() -> None:
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("username_key", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("publisher_name", sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column("publisher_key", sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column("api_key_hash", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("deleted_at", sa.String(length=24), nullable=True))
        batch_op.drop_column("can_publish")

    accounts = sa.table(
        "accounts",
        sa.column("username", sa.String),
        sa.column("username_key", sa.String),
        sa.column("kind", sa.String),
        sa.column("created_at", sa.String),
    )
    op.execute(accounts.update().values(username_key=sa.func.lower(accounts.c.username)))

    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.alter_column("username_key", existing_type=sa.String(length=32), nullable=False)
        batch_op.create_unique_constraint(batch_op.f("uq_accounts_username_key"), ["username_key"])
        batch_op.create_unique_constraint(
            batch_op.f("uq_accounts_publisher_key"), ["publisher_key"]
        )
        batch_op.create_unique_constraint(batch_op.f("uq_accounts_api_key_hash"), ["api_key_hash"])

    op.bulk_insert(
        accounts,
        [
            {
                "username": "anonymous",
                "username_key": "anonymous",
                "kind": "human",
                "created_at": _utc_now_text(),
            }
        ],
    )


def _upgrade_items() -> None:
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.add_column(sa.Column("publisher", sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column("publisher_key", sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column("submitter_ip_hash", sa.String(length=64), nullable=True))
        batch_op.add_column(
            sa.Column("unique_clicks", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.create_index(batch_op.f("ix_items_publisher_key"), ["publisher_key"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_items_submitter_ip_hash"), ["submitter_ip_hash"], unique=False
        )


def _create_item_links() -> None:
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
        "item_related_urls",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("canonical_url", sa.String(length=2048), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("origin", _enum("relationorigin", "submitted", "jev"), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_item_related_urls_item_id_items")
        ),
        sa.PrimaryKeyConstraint("item_id", "canonical_url", name=op.f("pk_item_related_urls")),
    )
    with op.batch_alter_table("item_related_urls", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_item_related_urls_canonical_url"), ["canonical_url"], unique=False
        )


def _create_sessions() -> None:
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


def _create_votes_and_clicks() -> None:
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


def _create_flags() -> None:
    op.create_table(
        "flags",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.String(length=24), nullable=False),
        sa.Column("updated_at", sa.String(length=24), nullable=False),
        sa.Column("resolved_at", sa.String(length=24), nullable=True),
        sa.Column("resolution", _enum("flagresolution", "dismissed", "deleted"), nullable=True),
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


def _create_submission_checks() -> None:
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
            _enum("checkoutcome", "published", "off_topic", "duplicate", "unavailable"),
            nullable=False,
        ),
        sa.Column("on_topic_probability", sa.Float(), nullable=True),
        sa.Column("relation", _enum("storyrelation", "same", "update", "different"), nullable=True),
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


def _create_rate_events() -> None:
    op.create_table(
        "rate_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "action",
            _enum("rateaction", "submit", "vote", "click", "comment", "flag", "signup", "login"),
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


def downgrade() -> None:
    op.drop_table("rate_events")
    op.drop_table("submission_checks")
    op.drop_table("flags")
    op.drop_table("item_impressions_daily")
    op.drop_table("click_events")
    op.drop_table("vote_events")
    op.drop_table("votes")
    op.drop_table("sessions")
    op.drop_table("item_related_urls")
    op.drop_table("item_corroborating_urls")

    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_items_submitter_ip_hash"))
        batch_op.drop_index(batch_op.f("ix_items_publisher_key"))
        batch_op.drop_column("unique_clicks")
        batch_op.drop_column("submitter_ip_hash")
        batch_op.drop_column("publisher_key")
        batch_op.drop_column("publisher")

    op.execute("DELETE FROM accounts WHERE username = 'anonymous'")
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("uq_accounts_api_key_hash"), type_="unique")
        batch_op.drop_constraint(batch_op.f("uq_accounts_publisher_key"), type_="unique")
        batch_op.drop_constraint(batch_op.f("uq_accounts_username_key"), type_="unique")
        batch_op.add_column(
            sa.Column("can_publish", sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.drop_column("deleted_at")
        batch_op.drop_column("api_key_hash")
        batch_op.drop_column("publisher_key")
        batch_op.drop_column("publisher_name")
        batch_op.drop_column("username_key")

    with op.batch_alter_table("topics", schema=None) as batch_op:
        batch_op.drop_column("description")
