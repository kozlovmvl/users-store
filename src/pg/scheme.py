from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import UUID as SA_UUID, ForeignKey, String


class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True


class UserSchema(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(SA_UUID, primary_key=True, default=uuid4())
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)


class PasswordSchema(Base):
    __tablename__ = "passwords"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    value: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
