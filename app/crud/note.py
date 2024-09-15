from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.note import Note, Tag
from app.schemas.note import NoteCreate
from app.models.note import note_tags  # Импорт ассоциационной таблицы



# Асинхронная функция для получения заметок пользователя
async def get_notes(db: AsyncSession, user_id: int):
    # result = await db.execute(select(Note).where(Note.user_id == user_id))
    # return result.scalars().all()  # Возвращаем все найденные заметки

    result = await db.execute(
        select(Note).where(Note.user_id == user_id).options(selectinload(Note.tags))
    )
    return result.scalars().all()  # Возвращаем все найденные заметки


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


# Асинхронная функция для обновления заметки
async def update_note(db: AsyncSession, note_id: int, note_in: NoteCreate, user_id: int):
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == user_id).options(selectinload(Note.tags))
    )
    note = result.scalars().first()

    if not note:
        return None  # Если заметка не найдена или принадлежит другому пользователю

    # Обновляем поля заметки
    note.title = note_in.title
    note.content = note_in.content

    # Обрабатываем теги
    tags = []
    for tag_name in note_in.tags:
        tag = await db.execute(select(Tag).where(Tag.name == tag_name))
        tag = tag.scalars().first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        tags.append(tag)

    note.tags = tags  # Обновляем теги

    await db.commit()  # Асинхронный коммит
    await db.refresh(note)  # Обновляем объект заметки
    return note


# # Асинхронная функция для удаления заметки
# async def delete_note(db: AsyncSession, note_id: int, user_id: int):
#     result = await db.execute(
#         select(Note).where(Note.id == note_id, Note.user_id == user_id)
#     )
#     note = result.scalars().first()
#
#     if not note:
#         return None  # Если заметка не найдена или принадлежит другому пользователю
#
#     await db.execute(delete(Note).where(Note.id == note_id))
#     await db.commit()  # Асинхронный коммит
#     return note


# Асинхронная функция для удаления заметки
async def delete_note(db: AsyncSession, note_id: int, user_id: int):
    # Проверяем, существует ли заметка и принадлежит ли она текущему пользователю
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    note = result.scalars().first()

    if not note:
        return None  # Заметка не найдена или принадлежит другому пользователю

    # Удаляем связанные записи из таблицы note_tags
    await db.execute(
        delete(note_tags).where(note_tags.c.note_id == note_id)
    )

    # Удаляем саму заметку
    await db.execute(delete(Note).where(Note.id == note_id))

    # Фиксируем изменения в базе данных
    await db.commit()

    return note