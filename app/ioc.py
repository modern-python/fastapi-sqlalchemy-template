from modern_di import Group, Scope, providers

from app import repositories
from app.resources.db import create_sa_engine, create_session


class Dependencies(Group):
    database_engine = providers.Resource(Scope.APP, create_sa_engine)
    session = providers.Resource(Scope.REQUEST, create_session, engine=database_engine.cast)

    decks_service = providers.Factory(Scope.REQUEST, repositories.DecksService, session=session.cast, auto_commit=True)
    cards_service = providers.Factory(Scope.REQUEST, repositories.CardsService, session=session.cast, auto_commit=True)
