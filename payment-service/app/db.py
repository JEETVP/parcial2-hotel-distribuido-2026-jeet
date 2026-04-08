"""Conexión async a Postgres para payment-service."""

# BUG: credenciales hardcodeadas. Esto es un problema de seguridad y de
# configuración: no puedes cambiarlas sin reconstruir la imagen, y dejarlas
# así en un repo público equivale a publicar tus contraseñas.
#
# Mira availability-service/app/db.py para ver cómo se construye la URL
# leyendo POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, etc. con os.getenv().
# Las variables ya están en .env.example.
DATABASE_URL = "postgresql+asyncpg://hotel_user:hotel_pass@postgres:5432/hotel_db"

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)


engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
