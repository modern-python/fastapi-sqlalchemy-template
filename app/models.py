import datetime
import logging
import typing

import sqlalchemy as sa
from sqlalchemy import orm

from app.helpers.datetime import generate_utc_dt


logger = logging.getLogger(__name__)


METADATA: typing.Final = sa.MetaData()


class Base(orm.DeclarativeBase):
    metadata = METADATA


class BaseModel(Base):
    __abstract__ = True

    id: orm.Mapped[typing.Annotated[int, orm.mapped_column(primary_key=True)]]
    created_at: orm.Mapped[
        typing.Annotated[
            datetime.datetime,
            orm.mapped_column(sa.DateTime(timezone=True), default=generate_utc_dt, nullable=False),
        ]
    ]
    updated_at: orm.Mapped[
        typing.Annotated[
            datetime.datetime,
            orm.mapped_column(sa.DateTime(timezone=True), default=generate_utc_dt, nullable=False),
        ]
    ]

    def __str__(self) -> str:
        return f"<{type(self).__name__}({self.id=})>"


class Deck(BaseModel):
    __tablename__ = "decks"

    name: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    description: orm.Mapped[str | None] = orm.mapped_column(sa.String, nullable=True)
    cards: orm.Mapped[list["Card"]] = orm.relationship("Card", lazy="noload", uselist=True)


class Card(BaseModel):
    __tablename__ = "cards"
    __table_args__ = (sa.UniqueConstraint("deck_id", "front", name="card_deck_id_front_uc"),)

    front: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    back: orm.Mapped[str | None] = orm.mapped_column(sa.String, nullable=True)
    hint: orm.Mapped[str | None] = orm.mapped_column(sa.String, nullable=True)
    deck_id: orm.Mapped[int] = orm.mapped_column(sa.Integer, sa.ForeignKey("decks.id"))
