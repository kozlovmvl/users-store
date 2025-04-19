from uuid import UUID
from typing import Protocol, runtime_checkable
from users_core.models import User
from pg.scheme import UserSchema
from sqlalchemy import delete, select
from pg.core import AsyncSessionMaker


@runtime_checkable
class UserRepositoryProtocol(Protocol):
    async def get_by_id(self, user_id: UUID) -> User: ...

    async def create(self, user: User) -> None: ...

    async def update(self, user: User) -> None: ...

    async def delete(self, user: User) -> None: ...


class UserRepository:
    def __init__(self, async_session_maker: AsyncSessionMaker):
        self.async_session_maker = async_session_maker

    async def get_by_id(self, user_id: UUID) -> User:
        async with self.async_session_maker() as session:
            stmt = select(UserSchema).where(UserSchema.id == user_id)
            result = (await session.execute(stmt)).scalar_one()
            return User.model_validate(result)

    async def create(self, user: User) -> None:
        async with self.async_session_maker() as session:
            user_schema = UserSchema(
                id=user.id, username=user.username, email=user.email
            )
            session.add(user_schema)
            await session.commit()

    async def update(self, user: User) -> None:
        async with self.async_session_maker() as session:
            user_schema = (
                await session.execute(
                    select(UserSchema).where(UserSchema.id == user.id)
                )
            ).scalar_one()
            for key, value in user.model_dump().items():
                setattr(user_schema, key, value)
            await session.commit()

    async def delete(self, user: User) -> None:
        async with self.async_session_maker() as session:
            await session.execute(delete(UserSchema).where(UserSchema.id == user.id))
