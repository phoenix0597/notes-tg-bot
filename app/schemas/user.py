# app/schemas/user.py
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: Optional[EmailStr]
    telegram_id: Optional[int]

class UserCreate(UserBase):
    password: Optional[str]
    telegram_id: Optional[int]

class UserInDB(UserBase):
    id: int
    is_active: bool


    model_config = ConfigDict(arbitrary_types_allowed=True)
