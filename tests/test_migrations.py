import typing

import sqlalchemy as sa
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext

from app.models import METADATA
from app.resources.db import create_primary_sa_engine


def _compare_with_models(connection: sa.Connection) -> list[typing.Any]:
    return compare_metadata(MigrationContext.configure(connection), METADATA)


async def test_migrations_match_models() -> None:
    engine: typing.Final = create_primary_sa_engine()
    try:
        async with engine.connect() as connection:
            diff = await connection.run_sync(_compare_with_models)
    finally:
        await engine.dispose()

    assert diff == []


async def test_id_sequences_are_bigint() -> None:
    engine: typing.Final = create_primary_sa_engine()
    try:
        async with engine.connect() as connection:
            sequence_types = dict(
                (await connection.execute(sa.text("SELECT sequence_name, data_type FROM information_schema.sequences")))
                .tuples()
                .all()
            )
    finally:
        await engine.dispose()

    assert sequence_types == {"decks_id_seq": "bigint", "cards_id_seq": "bigint"}
