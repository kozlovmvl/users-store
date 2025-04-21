import pytest
from sqlalchemy import exists, select
from users_core.models import Password

from pg.repositories import PasswordRepository
from pg.scheme import PasswordSchema


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_obj(mock_session_maker, mock_password):
    repo = PasswordRepository(async_session_maker=mock_session_maker)
    result = await repo.get_by_obj(raw_obj=mock_password)
    assert result.user_id == mock_password.user_id


@pytest.mark.asyncio(loop_scope="session")
async def test_create_password(mock_session_maker, mock_user):
    repo = PasswordRepository(async_session_maker=mock_session_maker)
    password = Password(user_id=mock_user.id, raw="Pass@12345")
    await repo.create(password)

    async with mock_session_maker() as session:
        password_schema = (
            await session.execute(
                select(PasswordSchema).where(PasswordSchema.user_id == password.user_id)
            )
        ).scalar_one()
        assert password_schema.hash == password.hash


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_password(mock_session_maker, mock_password):
    repo = PasswordRepository(async_session_maker=mock_session_maker)
    await repo.delete(mock_password)

    async with mock_session_maker() as session:
        to_exist = await session.scalar(
            select(exists().where(PasswordSchema.user_id == mock_password.user_id))
        )
        assert not to_exist
