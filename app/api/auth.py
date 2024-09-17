# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, Response, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, create_access_token
# from app.models.user import User
from app.schemas.user import UserCreate, UserInDB
from app.crud.user import (get_user_by_email, get_user_by_telegram_id,
                           create_user, create_user_by_telegram_id)
from app.api.deps import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Пользователи"],
)


@router.post("/register", response_model=UserInDB)
async def register_new_user(
        user_in: UserCreate = None,
        db: AsyncSession = Depends(get_db)
):

    # Стандартная регистрация по email и паролю
    if user_in:
        existing_user = await get_user_by_email(db, user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

    user = await create_user(db=db, user_in=user_in)
    return user

@router.post("/register/telegram", response_model=UserInDB)
async def register_new_user_by_telegram(
        # telegram_id: int,
        telegram_id: int = Header(...),  # Извлекаем telegram_id из заголовка
        db: AsyncSession = Depends(get_db)
):
    existing_user = await get_user_by_telegram_id(db, telegram_id)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this Telegram ID already exists")

    # Создаем нового пользователя с Telegram ID
    new_user = await create_user_by_telegram_id(db, telegram_id)
    return new_user



@router.post("/login")
async def login_for_access_token(
        response: Response,
        form_data: UserCreate = None,  # Для логина по email
        telegram_id: int = None,  # Для логина по Telegram ID

        db: AsyncSession = Depends(get_db)
):
    user = None

    # Логин по Telegram ID
    if telegram_id:
        user = await get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid Telegram ID")

    # Логин по email и паролю
    elif form_data:
        user = await get_user_by_email(db, form_data.email)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid email or password")

    # Если не указаны ни email, ни Telegram ID
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Генерация токена
    access_token = create_access_token(data={"sub": user.email})  # используем email как уникальный идентификатор
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return {"access_token": access_token, "token_type": "bearer"}


# @router.get("/telegram/{telegram_id}")
# async def get_user_by_telegram_id_route(telegram_id: int, db: AsyncSession = Depends(get_db)):
#     user = await get_user_by_telegram_id(db=db, telegram_id=telegram_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"id": user.id, "email": user.email}