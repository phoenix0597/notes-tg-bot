from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.note import Note
from app.schemas.note import NoteCreate


# Асинхронная функция для создания новой заметки
async def create_note(db: AsyncSession, note_in: NoteCreate, user_id: int):
    # note = Note(**note_in.dict(), user_id=user_id)
    note = Note(**note_in.model_dump(), user_id=user_id)
    db.add(note)
    await db.commit()  # Асинхронный коммит
    await db.refresh(note)
    return note


# Асинхронная функция для получения заметок пользователя
async def get_notes(db: AsyncSession, user_id: int):
    result = await db.execute(select(Note).where(Note.user_id == user_id))
    return result.scalars().all()  # Возвращаем все найденные заметки
