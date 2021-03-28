from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def transaction(session: AsyncSession):
    """hack to migrate from the sub transaction pattern
    https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#migrating-from-the-subtransaction-pattern
    """
    if not session.in_transaction():
        async with session.begin():
            yield
    else:
        yield
