from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


# Асинхронное создание пользователя
async def create_user(db: AsyncSession, user_in: UserCreate):
    hashed_password = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# Асинхронное получение пользователя по email
async def get_user_by_email(db: AsyncSession, email: EmailStr):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()
