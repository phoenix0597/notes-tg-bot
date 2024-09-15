from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, create_access_token
from app.schemas.user import UserCreate, UserInDB
from app.crud.user import get_user_by_email, create_user
from app.api.deps import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Пользователи"],
)


@router.post("/register", response_model=UserInDB)
async def register_new_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user = await create_user(db=db, user_in=user_in)
    return user


@router.post("/login")
async def login_for_access_token(response: Response,
        form_data: UserCreate, db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, form_data.email)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}
