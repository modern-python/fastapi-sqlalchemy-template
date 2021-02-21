import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db import Base


class Deck(Base):
    name = sa.Column(sa.String, nullable=False, unique=True)
    description = sa.Column(sa.String, nullable=True)
    cards = relationship("Card")
    tests = relationship("Test")


class Card(Base):
    front = sa.Column(sa.String, nullable=False, unique=True)
    back = sa.Column(sa.String, nullable=True)
    hint = sa.Column(sa.String, nullable=True)
    deck_id = sa.Column(sa.Integer, sa.ForeignKey("deck.id"))


class Test(Base):
    question = sa.Column(sa.String, nullable=False, unique=True)
    options = sa.Column(sa.String, nullable=True)
    hint = sa.Column(sa.String, nullable=True)
    deck_id = sa.Column(sa.Integer, sa.ForeignKey("deck.id"))
