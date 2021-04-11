from sqlalchemy.exc import PendingRollbackError

from app.db import async_session


async def get_db():
    session = async_session()
    try:
        yield session
        try:
            await session.commit()
        except PendingRollbackError:
            pass
    finally:
        await session.close()
