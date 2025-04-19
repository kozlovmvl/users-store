import pytest_asyncio
from pg.core import async_engine
from pg.scheme import Base, UserSchema
from sqlalchemy.ext.asyncio import async_sessionmaker

from users_core.models import User


@pytest_asyncio.fixture(loop_scope="session")
async def mock_session_maker():
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

        yield async_sessionmaker(bind=connection, expire_on_commit=False)

        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(loop_scope="session")
async def mock_user(mock_session_maker):
    async with mock_session_maker() as session:
        user_schema = UserSchema(username="user1", email="user1@host")
        session.add(user_schema)
        await session.commit()
    yield User.model_validate(user_schema)
