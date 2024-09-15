from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Асинхронный движок базы данных
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Создание асинхронной сессии
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False
)

class Base(DeclarativeBase):
    pass


# Функция для получения асинхронной сессии
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session