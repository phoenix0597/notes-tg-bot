from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(arbitrary_types_allowed=True)
