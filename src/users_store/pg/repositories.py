from typing import Protocol, runtime_checkable
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from users_core.models import Password, User

from users_store.pg.core import AsyncSessionMaker
from users_store.pg.exc import DuplicateUserKey, PasswordNotFound, UserNotFound
from users_store.pg.scheme import PasswordSchema, UserSchema


@runtime_checkable
class UserRepositoryProtocol(Protocol):
    async def get_by_id(self, user_id: UUID) -> User: ...

    async def get_by_username(self, username: str) -> User: ...

    async def create(self, user: User) -> None: ...

    async def update(self, user: User) -> None: ...

    async def delete(self, user: User) -> None: ...


@runtime_checkable
class PasswordRepositoryProtocol(Protocol):
    async def get_by_obj(self, raw_obj: Password) -> Password: ...

    async def create(self, password: Password) -> None: ...

    async def delete(self, password: Password) -> None: ...


class UserRepository:
    def __init__(self, async_session_maker: AsyncSessionMaker):
        self.async_session_maker = async_session_maker

    async def get_by_id(self, user_id: UUID) -> User:
        stmt = select(UserSchema).where(UserSchema.id == user_id)
        async with self.async_session_maker() as session:
            try:
                result = (await session.execute(stmt)).scalar_one()
            except NoResultFound as err:
                raise UserNotFound from err
            return User.model_validate(result)

    async def get_by_username(self, username: str) -> User:
        stmt = select(UserSchema).where(UserSchema.username == username)
        async with self.async_session_maker() as session:
            try:
                result = (await session.execute(stmt)).scalar_one()
            except NoResultFound as err:
                raise UserNotFound from err
            return User.model_validate(result)

    async def create(self, user: User) -> None:
        user_schema = UserSchema(id=user.id, username=user.username, email=user.email)
        async with self.async_session_maker() as session:
            session.add(user_schema)
            try:
                await session.commit()
            except IntegrityError as err:
                raise DuplicateUserKey from err

    async def update(self, user: User) -> None:
        stmt = select(UserSchema).where(UserSchema.id == user.id)
        async with self.async_session_maker() as session:
            try:
                user_schema = (await session.execute(stmt)).scalar_one()
            except NoResultFound as err:
                raise UserNotFound from err
            for key, value in user.model_dump().items():
                setattr(user_schema, key, value)
            try:
                await session.commit()
            except IntegrityError as err:
                raise DuplicateUserKey from err

    async def delete(self, user: User) -> None:
        stmt = delete(UserSchema).where(UserSchema.id == user.id)
        async with self.async_session_maker() as session:
            await session.execute(stmt)


class PasswordRepository:
    def __init__(self, async_session_maker: AsyncSessionMaker):
        self.async_session_maker = async_session_maker

    async def get_by_obj(self, raw_obj: Password) -> Password:
        stmt = select(PasswordSchema).where(
            PasswordSchema.user_id == raw_obj.user_id,
            PasswordSchema.hash == raw_obj.hash,
        )
        async with self.async_session_maker() as session:
            try:
                result = (await session.execute(stmt)).scalar_one()
            except NoResultFound as err:
                raise PasswordNotFound from err
        return Password.model_validate(result)

    async def create(self, password: Password) -> None:
        password_schema = PasswordSchema(
            user_id=password.user_id, hash=password.hash, created_at=password.created_at
        )
        async with self.async_session_maker() as session:
            try:
                session.add(password_schema)
                await session.commit()
            except IntegrityError as err:
                raise UserNotFound from err

    async def delete(self, password: Password) -> None:
        stmt = delete(PasswordSchema).where(PasswordSchema.user_id == password.user_id)
        async with self.async_session_maker() as session:
            await session.execute(stmt)
