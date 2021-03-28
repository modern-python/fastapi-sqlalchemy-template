from app.db import async_session


async def get_db():
    session = async_session()
    try:
        yield session
        await session.commit()
    finally:
        await session.close()
