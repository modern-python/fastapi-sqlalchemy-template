import typing
import uuid

import sqlalchemy as sa
from advanced_alchemy.base import BigIntAuditBase, orm_registry
from sqlalchemy import orm


METADATA: typing.Final = orm_registry.metadata
orm.DeclarativeBase.metadata = METADATA


class Deck(BigIntAuditBase):
    __tablename__ = "decks"
    __table_args__ = (sa.UniqueConstraint("idempotency_key", name="deck_idempotency_key_uc"),)

    idempotency_key: orm.Mapped[uuid.UUID] = orm.mapped_column(sa.Uuid, nullable=False)
    name: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    description: orm.Mapped[str | None] = orm.mapped_column(sa.String, nullable=True)
    cards: orm.Mapped[list[Card]] = orm.relationship("Card", lazy="noload", uselist=True, order_by="Card.id")


class Card(BigIntAuditBase):
    __tablename__ = "cards"
    __table_args__ = (
        sa.UniqueConstraint("deck_id", "front", name="card_deck_id_front_uc"),
        sa.Index("ix_cards_deck_id_id", "deck_id", "id"),
    )

    front: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    back: orm.Mapped[str | None] = orm.mapped_column(sa.String, nullable=True)
    hint: orm.Mapped[str | None] = orm.mapped_column(sa.String, nullable=True)
    deck_id: orm.Mapped[int] = orm.mapped_column(sa.BigInteger, sa.ForeignKey("decks.id"))
