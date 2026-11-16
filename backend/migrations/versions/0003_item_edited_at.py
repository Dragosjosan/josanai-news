from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | Sequence[str] | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # A plain ADD COLUMN keeps the table, so the search triggers on items stay in place.
    op.add_column("items", sa.Column("edited_at", sa.String(length=24), nullable=True))


def downgrade() -> None:
    op.drop_column("items", "edited_at")
