import typing

from db_retry import Transaction
from modern_di import Group, Scope, providers

from app.repositories import CardsRepository, DecksRepository
from app.resources.db import (
    autocommit_isolation_level,
    choose_sa_engine,
    close_sa_engine,
    close_session,
    create_sa_engine,
    create_session,
    read_engine_url,
)
from app.settings import Settings
from app.use_cases.create_cards import CreateCardsUseCase
from app.use_cases.create_deck import CreateDeckUseCase
from app.use_cases.get_card import GetCardUseCase
from app.use_cases.get_deck import GetDeckUseCase
from app.use_cases.list_cards import ListCardsUseCase
from app.use_cases.list_decks import ListDecksUseCase
from app.use_cases.update_cards import UpdateCardsUseCase
from app.use_cases.update_deck import UpdateDeckUseCase


class Config(Group):
    settings = providers.Factory(creator=Settings, cache=True)


class Database(Group):
    database_engine = providers.Factory(
        creator=create_sa_engine,
        cache=providers.CacheSettings(finalizer=close_sa_engine),
        bound_type=None,
        kwargs={"settings": Config.settings, "url": Config.settings.derive(lambda s: s.db_dsn_parsed)},
    )
    database_read_engine = providers.Factory(
        creator=create_sa_engine,
        cache=providers.CacheSettings(finalizer=close_sa_engine),
        bound_type=None,
        kwargs={"settings": Config.settings, "url": Config.settings.derive(read_engine_url), "read_only": True},
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
    autocommit_isolation_level = providers.Factory(creator=autocommit_isolation_level, bound_type=None)
    autocommit_transaction = providers.Factory(
        scope=Scope.REQUEST,
        creator=Transaction,
        bound_type=None,
        kwargs={"session": session, "isolation_level": autocommit_isolation_level},
    )


class Repositories(Group, scope=Scope.REQUEST):
    decks_repository = providers.Factory(
        creator=DecksRepository,
        kwargs={"session": Database.session, "auto_commit": False},
    )
    cards_repository = providers.Factory(
        creator=CardsRepository,
        kwargs={"session": Database.session, "auto_commit": False},
    )


class UseCases(Group, scope=Scope.REQUEST):
    list_decks_use_case = providers.Factory(creator=ListDecksUseCase)
    get_deck_use_case = providers.Factory(creator=GetDeckUseCase)
    update_deck_use_case = providers.Factory(
        creator=UpdateDeckUseCase, kwargs={"transaction": Database.autocommit_transaction}
    )
    create_deck_use_case = providers.Factory(
        creator=CreateDeckUseCase, kwargs={"transaction": Database.autocommit_transaction}
    )
    list_cards_use_case = providers.Factory(creator=ListCardsUseCase)
    get_card_use_case = providers.Factory(creator=GetCardUseCase)
    create_cards_use_case = providers.Factory(creator=CreateCardsUseCase)
    update_cards_use_case = providers.Factory(creator=UpdateCardsUseCase)


ALL_GROUPS: typing.Final[list[type[Group]]] = [Config, Database, Repositories, UseCases]
