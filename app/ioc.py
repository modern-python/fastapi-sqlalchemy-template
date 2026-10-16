from db_retry import Transaction
from modern_di import Group, Scope, providers

from app.repositories import CardsRepository, DecksRepository
from app.resources.db import (
    choose_sa_engine,
    close_sa_engine,
    close_session,
    create_primary_sa_engine,
    create_read_sa_engine,
    create_session,
)


class Dependencies(Group):
    database_engine = providers.Factory(
        creator=create_primary_sa_engine,
        cache=providers.CacheSettings(finalizer=close_sa_engine),
        bound_type=None,
    )
    database_read_engine = providers.Factory(
        creator=create_read_sa_engine,
        cache=providers.CacheSettings(finalizer=close_sa_engine),
        bound_type=None,
    )
    dynamic_engine = providers.Factory(
        scope=Scope.REQUEST,
        creator=choose_sa_engine,
        kwargs={"primary_engine": database_engine, "read_engine": database_read_engine},
    )
    session = providers.Factory(
        scope=Scope.REQUEST,
        creator=create_session,
        cache=providers.CacheSettings(finalizer=close_session),
        kwargs={"engine": dynamic_engine},
    )
    transaction = providers.Factory(
        scope=Scope.REQUEST,
        creator=Transaction,
        kwargs={"session": session},
    )

    decks_repository = providers.Factory(
        scope=Scope.REQUEST,
        creator=DecksRepository,
        kwargs={"auto_commit": False, "session": session},
    )
    cards_repository = providers.Factory(
        scope=Scope.REQUEST,
        creator=CardsRepository,
        kwargs={"auto_commit": False, "session": session},
    )
