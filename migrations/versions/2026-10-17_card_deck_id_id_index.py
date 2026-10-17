"""card deck_id id index.

Revision ID: 4004ffe4656f
Revises: 8e4a2c7b1f6d
Create Date: 2026-10-17 12:13:24.538852

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "4004ffe4656f"
down_revision = "8e4a2c7b1f6d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_cards_deck_id_id", "cards", ["deck_id", "id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_cards_deck_id_id", table_name="cards")
