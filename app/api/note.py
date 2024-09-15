from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.note import NoteCreate, NoteInDB
from app.crud.note import create_note, get_notes
from app.api.deps import get_db, get_current_user

router = APIRouter(
    prefix="/notes",
    tags=["Заметки"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=NoteInDB)
async def create_new_note(
    note_in: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    return await create_note(db=db, note_in=note_in, user_id=current_user.id)

@router.get("/", response_model=List[NoteInDB])
async def read_notes(
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    return await get_notes(db=db, user_id=current_user.id)
