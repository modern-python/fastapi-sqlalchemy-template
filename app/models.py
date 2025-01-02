import typing

import sqlalchemy as sa
from advanced_alchemy.base import BigIntAuditBase, orm_registry
from sqlalchemy import orm


METADATA: typing.Final = orm_registry.metadata
orm.DeclarativeBase.metadata = METADATA


class Deck(BigIntAuditBase):
    __tablename__ = "decks"

    name: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    description: orm.Mapped[str | None] = orm.mapped_column(sa.String, nullable=True)
    cards: orm.Mapped[list["Card"]] = orm.relationship("Card", lazy="noload", uselist=True)


class Card(BigIntAuditBase):
    __tablename__ = "cards"
    __table_args__ = (sa.UniqueConstraint("deck_id", "front", name="card_deck_id_front_uc"),)

    front: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    back: orm.Mapped[str | None] = orm.mapped_column(sa.String, nullable=True)
    hint: orm.Mapped[str | None] = orm.mapped_column(sa.String, nullable=True)
    deck_id: orm.Mapped[int] = orm.mapped_column(sa.Integer, sa.ForeignKey("decks.id"))
