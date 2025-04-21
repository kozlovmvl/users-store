from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from users_store.pg.settings import settings

db_url = URL.create(
    drivername="postgresql+asyncpg",
    host=settings.POSTRGES_HOST,
    port=settings.POSTGRES_PORT,
    database=settings.POSTGRES_DB,
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
)

type AsyncSessionMaker = async_sessionmaker[AsyncSession]
async_engine = create_async_engine(url=db_url)
async_session_maker: AsyncSessionMaker = async_sessionmaker(
    engine=async_engine, expire_on_commit=False
)
