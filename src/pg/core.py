from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import URL

from pg.settings import settings

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
