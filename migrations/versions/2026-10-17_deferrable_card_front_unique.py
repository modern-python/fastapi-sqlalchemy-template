"""deferrable card front unique.

Revision ID: 456d08f790fb
Revises: 4004ffe4656f
Create Date: 2026-10-17 15:00:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "456d08f790fb"
down_revision = "4004ffe4656f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("card_deck_id_front_uc", "cards", type_="unique")
    op.create_unique_constraint(
        "card_deck_id_front_uc", "cards", ["deck_id", "front"], deferrable=True, initially="IMMEDIATE"
    )


def downgrade() -> None:
    op.drop_constraint("card_deck_id_front_uc", "cards", type_="unique")
    op.create_unique_constraint("card_deck_id_front_uc", "cards", ["deck_id", "front"])
