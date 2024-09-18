from typing import List

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.models.note import Note, Tag
from app.schemas.note import NoteCreate
from app.models.note import note_tags  # Импорт ассоциационной таблицы


# Вспомогательная асинхронная функция для получения или создания тегов
async def get_or_create_tags(db: AsyncSession, tag_names: list[str]):
    tags = []
    for tag_name in tag_names:
        result = await db.execute(select(Tag).where(Tag.name == tag_name))
        tag = result.scalars().first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        tags.append(tag)
    return tags


# Асинхронная функция для получения заметок пользователя
async def get_notes(db: AsyncSession, user_id: int):
    query = select(Note).where(Note.user_id == user_id).options(selectinload(Note.tags))
    result = await db.execute(query)
    return result.scalars().all()  # Возвращаем все найденные заметки


# Асинхронная функция для поиска заметок по тегам
async def search_notes(db: AsyncSession, user_id: int, tags: List[str]):
    # Количество тегов для фильтрации
    tags_count = len(tags)

    # Запрос для поиска заметок, которые содержат все переданные теги
    query = (
        select(Note)
        .join(Note.tags)  # Присоединяем таблицу тегов
        .where(Note.user_id == user_id)  # Фильтруем заметки по ID пользователя
        .where(Tag.name.in_(tags))  # Ищем заметки с хотя бы одним из тегов
        .group_by(Note.id)  # Группируем по заметке
        .having(func.count(Tag.id) == tags_count)  # Убедимся, что все теги присутствуют
        .options(selectinload(Note.tags))  # Загружаем теги вместе с заметками
    )

    # # Запрос для поиска заметок, которые содержат хотя бы один из переданных тегов
    # query = (
    #     select(Note)
    #     .join(Note.tags)  # Присоединяем таблицу тегов
    #     .where(Note.user_id == user_id)  # Фильтруем заметки по ID пользователя
    #     .where(Tag.name.in_(tags))  # Ищем заметки, где хотя бы один тег совпадает
    #     .group_by(Note.id)  # Группируем по заметке
    #     .options(selectinload(Note.tags))  # Загружаем теги вместе с заметками
    # )
    #

    result = await db.execute(query)
    return result.scalars().all()  # Возвращаем все найденные заметки


# Асинхронная функция для создания новой заметки
async def create_note(db: AsyncSession, note_in: NoteCreate, user_id: int):
    # Получаем или создаем теги
    tags = await get_or_create_tags(db, note_in.tags)
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

    # Обновляем теги
    note.tags = await get_or_create_tags(db, note_in.tags)

    await db.commit()  # Асинхронный коммит
    await db.refresh(note)  # Обновляем объект заметки
    return note


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
