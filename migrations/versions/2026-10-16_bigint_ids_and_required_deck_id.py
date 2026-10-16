"""bigint ids and required deck_id.

Revision ID: 8e4a2c7b1f6d
Revises: 5d1c0f3a9b2e
Create Date: 2026-10-16 22:00:00.000000

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "8e4a2c7b1f6d"
down_revision = "5d1c0f3a9b2e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("decks", "id", type_=sa.BigInteger(), existing_type=sa.Integer(), existing_nullable=False)
    op.execute("ALTER SEQUENCE decks_id_seq AS bigint")
    op.alter_column("cards", "id", type_=sa.BigInteger(), existing_type=sa.Integer(), existing_nullable=False)
    op.execute("ALTER SEQUENCE cards_id_seq AS bigint")
    op.alter_column("cards", "deck_id", type_=sa.BigInteger(), existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    op.alter_column("cards", "deck_id", type_=sa.Integer(), existing_type=sa.BigInteger(), nullable=True)
    op.execute("ALTER SEQUENCE cards_id_seq AS integer")
    op.alter_column("cards", "id", type_=sa.Integer(), existing_type=sa.BigInteger(), existing_nullable=False)
    op.execute("ALTER SEQUENCE decks_id_seq AS integer")
    op.alter_column("decks", "id", type_=sa.Integer(), existing_type=sa.BigInteger(), existing_nullable=False)
