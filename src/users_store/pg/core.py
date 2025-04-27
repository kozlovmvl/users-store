from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

type AsyncSessionMaker = async_sessionmaker[AsyncSession]


def engine_factory(
    postgres_host: str,
    postgres_port: int,
    postgres_db: str,
    postgres_user: str,
    postgres_password: str,
) -> AsyncEngine:
    db_url = URL.create(
        drivername="postgresql+asyncpg",
        host=postgres_host,
        port=postgres_port,
        database=postgres_db,
        username=postgres_user,
        password=postgres_password,
    )
    return create_async_engine(url=db_url)


def session_maker_factory(engine) -> AsyncSessionMaker:
    return async_sessionmaker(bind=engine, expire_on_commit=False)
