import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class Deck(Base):
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=True)
    cards = relationship("Card")
    tests = relationship("Test")


class Card(Base):
    front = sa.Column(sa.String, nullable=False)
    back = sa.Column(sa.String, nullable=True)
    hint = sa.Column(sa.String, nullable=True)
    deck_id = sa.Column(sa.Integer, sa.ForeignKey("deck.id"))
    __table_args__ = (
        UniqueConstraint("deck_id", "front", name="card_deck_id_front_uc"),
    )


class Test(Base):
    question = sa.Column(sa.String, nullable=False)
    options = sa.Column(sa.String, nullable=True)
    hint = sa.Column(sa.String, nullable=True)
    deck_id = sa.Column(sa.Integer, sa.ForeignKey("deck.id"))
    __table_args__ = (
        UniqueConstraint(
            "deck_id", "question", name="card_deck_id_question_uc"
        ),
    )
