from typing import List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TagBase(BaseModel):
    name: str


class TagInDB(TagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class NoteBase(BaseModel):
    title: str
    content: str
    # tags: str


class NoteCreate(NoteBase):
    tags: List[str]  # При создании заметки можно передать список тегов


class NoteInDB(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagInDB]  # Список тегов, связанных с заметкой

    model_config = ConfigDict(arbitrary_types_allowed=True)
