from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie, Header
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.config import settings
from app.db.base import get_db
from app.models.user import User
from app.crud.user import get_user_by_email, get_user_by_telegram_id
from pydantic import BaseModel


# Модель для токена
class TokenData(BaseModel):
    email: Optional[str] = None


async def get_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token


# Зависимость для получения текущего пользователя по токену или Telegram ID
async def get_current_user(
        db: AsyncSession = Depends(get_db),
        telegram_id: int = None,
        access_token: str = Cookie(None),  # Извлечение токена из куки
        authorization: str = Header(None)  # Извлечение токена из заголовка Authorization
) -> User:
    token = None
    if telegram_id:
        # Поиск пользователя по Telegram ID
        user = await get_user_by_telegram_id(db=db, telegram_id=telegram_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

    # На случай добавления клиентов (мобильных приложений или фронтенд-фреймворков
    # вроде React) оставим возможность передачи токена в заголовке
    elif authorization:
        print(authorization)
        # Если токен передан в заголовке Authorization
        scheme, _, param = authorization.partition(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        token = param

    elif access_token:
        # Если токен передан в куки
        token = access_token

    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            user = await get_user_by_email(db=db, email=email)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

    else:
        raise HTTPException(status_code=401, detail="Authorization credentials not provided")

    return user


# Зависимость для получения текущего активного пользователя (например, проверка блокировки аккаунта)
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
