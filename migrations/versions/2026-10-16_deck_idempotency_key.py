"""deck idempotency key.

Revision ID: 5d1c0f3a9b2e
Revises: abb62721e019
Create Date: 2026-10-16 20:00:00.000000

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "5d1c0f3a9b2e"
down_revision = "abb62721e019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "decks",
        sa.Column("idempotency_key", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
    )
    op.alter_column("decks", "idempotency_key", server_default=None)
    op.create_unique_constraint("deck_idempotency_key_uc", "decks", ["idempotency_key"])


def downgrade() -> None:
    op.drop_constraint("deck_idempotency_key_uc", "decks", type_="unique")
    op.drop_column("decks", "idempotency_key")
