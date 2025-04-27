import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker
from users_core.models import Password, User

from tests.pg.settings import settings
from users_store.pg.core import engine_factory
from users_store.pg.scheme import Base, PasswordSchema, UserSchema


@pytest_asyncio.fixture(loop_scope="session")
async def mock_session_maker():
    async_engine = engine_factory(**settings.model_dump())
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

        yield async_sessionmaker(bind=connection, expire_on_commit=False)

        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(loop_scope="session")
async def mock_user(mock_session_maker):
    user_schema = UserSchema(username="user1", email="user1@host")
    async with mock_session_maker() as session:
        session.add(user_schema)
        await session.commit()
    yield User.model_validate(user_schema)


@pytest_asyncio.fixture(loop_scope="session")
async def mock_password(mock_session_maker, mock_user):
    password = Password(user_id=mock_user.id, raw="Pass@12345")
    password_schema = PasswordSchema(
        user_id=password.user_id, hash=password.hash, created_at=password.created_at
    )
    async with mock_session_maker() as session:
        session.add(password_schema)
        await session.commit()
    yield password
