from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(arbitrary_types_allowed=True)
