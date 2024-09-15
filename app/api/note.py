from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.base import AsyncSessionLocal
from app.schemas.note import NoteCreate, NoteInDB
from app.crud.note import create_note, get_notes, update_note, delete_note
from app.api.deps import get_db, get_current_user

router = APIRouter(
    prefix="/notes",
    tags=["Заметки"],
)


@router.get("/", response_model=List[NoteInDB], status_code=status.HTTP_200_OK)
async def read_notes(
        db: AsyncSession = Depends(get_db),
        current_user: int = Depends(get_current_user)
):
    return await get_notes(db=db, user_id=current_user.id)


@router.post("/", response_model=NoteInDB, status_code=status.HTTP_201_CREATED)
async def create_new_note(
        note_in: NoteCreate,
        db: AsyncSession = Depends(get_db),
        current_user: int = Depends(get_current_user)
):
    return await create_note(db=db, note_in=note_in, user_id=current_user.id)


@router.put("/{note_id}", response_model=NoteInDB, status_code=status.HTTP_200_OK)
async def update_existing_note(
        note_id: int,
        note_in: NoteCreate,
        db: AsyncSession = Depends(get_db),
        current_user: int = Depends(get_current_user)
):
    note = await update_note(db=db, note_id=note_id, note_in=note_in, user_id=current_user.id)

    if not note:
        raise HTTPException(status_code=404, detail="Note not found or not authorized to update")

    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_note(
        note_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: int = Depends(get_current_user)
):
    note = await delete_note(db=db, note_id=note_id, user_id=current_user.id)

    if not note:
        raise HTTPException(status_code=404, detail="Note not found or not authorized to delete")

    return note
