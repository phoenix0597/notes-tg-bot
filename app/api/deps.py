# from typing import Generator, Optional
from typing import Optional
from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.config import settings
# from app.core.security import verify_password, get_password_hash
from app.db.base import get_db
from app.models.user import User
from app.crud.user import get_user_by_email
from pydantic import BaseModel


# Модель для токена
class TokenData(BaseModel):
    email: Optional[str] = None


async def get_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token


# Зависимость для получения текущего пользователя по токену
async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(get_token)
) -> User:

    print(f"Received token: {token}")  # Добавляем отладочное сообщение

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Декодируем токен
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    # Получаем пользователя по email
    user = await get_user_by_email(db=db, email=token_data.email)
    if user is None:
        raise credentials_exception

    return user


# Зависимость для получения текущего активного пользователя (например, проверка блокировки аккаунта)
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
