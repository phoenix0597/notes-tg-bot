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
        telegram_id: int = Header(None),
        access_token: str = Cookie(None),  # Извлечение токена из куки
        authorization: str = Header(None)  # Извлечение токена из заголовка Authorization
) -> User:
    token = None

    print(f"Received Telegram ID: {telegram_id=}")  # Отладочное сообщение

    # Если есть Telegram-ID в заголовке, ищем пользователя по нему
    if telegram_id:
        user = await get_user_by_telegram_id(db, telegram_id)
        if user:
            return user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Telegram ID")

    # На случай добавления клиентов (мобильных приложений или фронтенд-фреймворков
    # вроде React) оставим возможность передачи токена в заголовке
    elif authorization:
        print(authorization)
        # Если токен передан в заголовке Authorization
        scheme, _, param = authorization.partition(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid authentication scheme")
        token = param

    elif access_token:
        # Если токен передан в куки
        token = access_token

    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Invalid token payload")
            user = await get_user_by_email(db=db, email=email)
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Invalid credentials")
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token has expired")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authorization credentials not provided")

    return user


# Зависимость для получения текущего активного пользователя (например, проверка блокировки аккаунта)
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
