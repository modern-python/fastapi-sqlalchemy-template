import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.models import BaseModel


class Deck(BaseModel):
    __tablename__ = "deck"

    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=True)
    cards = relationship("Card", lazy="noload")


class Card(BaseModel):
    __tablename__ = "card"

    front = sa.Column(sa.String, nullable=False)
    back = sa.Column(sa.String, nullable=True)
    hint = sa.Column(sa.String, nullable=True)
    deck_id = sa.Column(sa.Integer, sa.ForeignKey("deck.id"))
    __table_args__ = (UniqueConstraint("deck_id", "front", name="card_deck_id_front_uc"),)
