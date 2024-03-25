"""init.

Revision ID: abb62721e019
Revises:
Create Date: 2021-05-08 08:24:57.850753

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "abb62721e019"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "decks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("front", sa.String(), nullable=False),
        sa.Column("back", sa.String(), nullable=True),
        sa.Column("hint", sa.String(), nullable=True),
        sa.Column("deck_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["deck_id"],
            ["decks.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("deck_id", "front", name="card_deck_id_front_uc"),
    )


def downgrade() -> None:
    op.drop_table("cards")
    op.drop_table("decks")
