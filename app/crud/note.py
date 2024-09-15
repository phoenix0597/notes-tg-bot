from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.note import Note, Tag
from app.schemas.note import NoteCreate


# Асинхронная функция для создания новой заметки
async def create_note(db: AsyncSession, note_in: NoteCreate, user_id: int):

    # Получаем или создаем теги
    tags = []
    for tag_name in note_in.tags:
        tag = await db.execute(select(Tag).where(Tag.name == tag_name))
        tag = tag.scalars().first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        tags.append(tag)

    # note = Note(**note_in.model_dump(), user_id=user_id)
    note = Note(title=note_in.title, content=note_in.content, user_id=user_id, tags=tags)


    db.add(note)
    await db.commit()  # Асинхронный коммит
    await db.refresh(note)
    return note


# Асинхронная функция для получения заметок пользователя
async def get_notes(db: AsyncSession, user_id: int):
    # result = await db.execute(select(Note).where(Note.user_id == user_id))
    # return result.scalars().all()  # Возвращаем все найденные заметки

    result = await db.execute(
        select(Note).where(Note.user_id == user_id).options(selectinload(Note.tags))
    )
    return result.scalars().all()  # Возвращаем все найденные заметки
