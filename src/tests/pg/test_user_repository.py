import pytest
from sqlalchemy import exists, select
from users_core.models import User

from pg.repositories import UserRepository
from pg.scheme import UserSchema


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_id(mock_session_maker, mock_user):
    repo = UserRepository(async_session_maker=mock_session_maker)
    user = await repo.get_by_id(user_id=mock_user.id)
    assert user.id == mock_user.id
    assert user.username == mock_user.username
    assert user.email == mock_user.email


@pytest.mark.asyncio(loop_scope="session")
async def test_create_user(mock_session_maker):
    repo = UserRepository(async_session_maker=mock_session_maker)
    user = User(username="user2", email="user2@host")
    await repo.create(user)

    async with mock_session_maker() as session:
        user_schema = (
            await session.execute(select(UserSchema).where(UserSchema.id == user.id))
        ).scalar_one()
        assert user_schema.username == user.username
        assert user_schema.email == user.email


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user(mock_session_maker, mock_user):
    repo = UserRepository(async_session_maker=mock_session_maker)
    user = await repo.get_by_id(user_id=mock_user.id)
    user.username = "user2"
    user.email = "user2@host"
    await repo.update(user)

    async with mock_session_maker() as session:
        user_schema = (
            await session.execute(select(UserSchema).where(UserSchema.id == user.id))
        ).scalar_one()
        assert user_schema.username == user.username
        assert user_schema.email == user.email


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user(mock_session_maker, mock_user):
    repo = UserRepository(async_session_maker=mock_session_maker)
    await repo.delete(mock_user)

    async with mock_session_maker() as session:
        to_exist = await session.scalar(
            select(exists().where(UserSchema.id == mock_user.id))
        )
        assert not to_exist
