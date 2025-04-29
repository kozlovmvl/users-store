import uuid

import pytest
from sqlalchemy import exists, select
from users_core.models import User

from users_store.pg.exc import DuplicateUserKey, UserNotFound
from users_store.pg.repositories import UserRepository
from users_store.pg.scheme import UserSchema


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_id_existing_user(mock_session_maker, mock_user):
    repo = UserRepository(async_session_maker=mock_session_maker)
    user = await repo.get_by_id(user_id=mock_user.id)
    assert user.id == mock_user.id
    assert user.username == mock_user.username
    assert user.email == mock_user.email


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_id_non_existent_user(mock_session_maker):
    repo = UserRepository(async_session_maker=mock_session_maker)
    with pytest.raises(UserNotFound):
        _ = await repo.get_by_id(user_id=uuid.uuid4())


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_username_existing_user(mock_session_maker, mock_user):
    repo = UserRepository(async_session_maker=mock_session_maker)
    user = await repo.get_by_username(username=mock_user.username)
    assert user.id == mock_user.id
    assert user.username == mock_user.username
    assert user.email == mock_user.email


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_username_non_existent_user(mock_session_maker):
    repo = UserRepository(async_session_maker=mock_session_maker)
    with pytest.raises(UserNotFound):
        _ = await repo.get_by_username(username="unknown")


@pytest.mark.asyncio(loop_scope="session")
async def test_create_unique_user(mock_session_maker):
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
async def test_create_non_unique_user(mock_session_maker, mock_user):
    repo = UserRepository(async_session_maker=mock_session_maker)
    with pytest.raises(DuplicateUserKey):
        await repo.create(mock_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_existing_user(mock_session_maker, mock_user):
    repo = UserRepository(async_session_maker=mock_session_maker)
    user = await repo.get_by_id(user_id=mock_user.id)
    user.username = "user3"
    user.email = "user3@host"
    await repo.update(user)

    async with mock_session_maker() as session:
        user_schema = (
            await session.execute(select(UserSchema).where(UserSchema.id == user.id))
        ).scalar_one()
        assert user_schema.username == user.username
        assert user_schema.email == user.email


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_non_existent_user(mock_session_maker, mock_user):
    repo = UserRepository(async_session_maker=mock_session_maker)
    mock_user.id = uuid.uuid4()
    with pytest.raises(UserNotFound):
        await repo.update(mock_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_update_non_unique_user(mock_session_maker, mock_user):
    repo = UserRepository(async_session_maker=mock_session_maker)
    mock_user.username = "user2"
    with pytest.raises(DuplicateUserKey):
        await repo.update(mock_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user(mock_session_maker, mock_user):
    repo = UserRepository(async_session_maker=mock_session_maker)
    await repo.delete(mock_user)

    async with mock_session_maker() as session:
        to_exist = await session.scalar(
            select(exists().where(UserSchema.id == mock_user.id))
        )
        assert not to_exist
