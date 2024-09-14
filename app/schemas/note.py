from pydantic import BaseModel, ConfigDict
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: str
    tags: str

class NoteCreate(NoteBase):
    pass

class NoteInDB(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    # class Config:
    #     orm_mode = True
    model_config = ConfigDict(arbitrary_types_allowed=True)
