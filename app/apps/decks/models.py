import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class Deck(Base):
    __tablename__ = "deck"

    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=True)
    # Lazy is workaround for async, use either "subquery" or "selectin"
    # More info:
    # - https://github.com/tiangolo/fastapi/pull/2331#issuecomment-801461215
    # - https://github.com/tiangolo/fastapi/pull/2331#issuecomment-807528963
    cards = relationship("Card", lazy="subquery")
    tests = relationship("Test", lazy="subquery")


class Card(Base):
    __tablename__ = "card"

    front = sa.Column(sa.String, nullable=False)
    back = sa.Column(sa.String, nullable=True)
    hint = sa.Column(sa.String, nullable=True)
    deck_id = sa.Column(sa.Integer, sa.ForeignKey("deck.id"))
    __table_args__ = (
        UniqueConstraint("deck_id", "front", name="card_deck_id_front_uc"),
    )


class Test(Base):
    __tablename__ = "test"

    question = sa.Column(sa.String, nullable=False)
    options = sa.Column(sa.String, nullable=True)
    hint = sa.Column(sa.String, nullable=True)
    deck_id = sa.Column(sa.Integer, sa.ForeignKey("deck.id"))
    __table_args__ = (
        UniqueConstraint(
            "deck_id", "question", name="card_deck_id_question_uc"
        ),
    )
