# telegram_bot/handlers.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from fastapi import Depends
# from telegram_bot.auth import authorize_user

import aiohttp

from app.core.config import settings as s
from telegram_bot.auth import authorize_user

router = Router()


# Определение состояний для FSM
class NoteForm(StatesGroup):
    waiting_for_title = State()     # состояние для ввода заголовка заметки
    waiting_for_content = State()   # состояние для ввода содержания заметки
    waiting_for_tags = State()      # состояние для ввода тегов к заметке



# Обработчик команды /start
@router.message(Command("start"))
async def start(message: types.Message):
    user = await authorize_user(message.from_user.id)

    print(f"\n{user=}\n")
    if user:
        # Пользователь найден, авторизован
        await message.answer(f"Привет, {user['telegram_id']}! "
                             f"Вы авторизованы и можете получать список заметок, или создавать новые."
                             f"Для получения справки, как это работает, введите /help")
    else:
        # Пользователь не найден, выполняем регистрацию
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"http://{s.BACKEND_HOST}:{s.BACKEND_PORT}/auth/register/telegram",
                    headers={"Telegram-ID": str(message.from_user.id)}) as response:

                print(f"\n{response=}\n")
                print(f"{await response.text()=}")  # Выводим тело ответа для диагностики

                if response.status == 200:
                    # Пользователь успешно зарегистрирован
                    await message.answer("Поздравляем, Вы зарегистрировались в приложении 'Мои заметки'! "
                                         "Для получения справки о работе с приложением введите /help")
                else:
                    await message.answer("Произошла ошибка при регистрации. Попробуйте снова позже.")


# Получение списка заметок
@router.message(Command("notes"))
async def get_notes(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{s.BACKEND_HOST}:{s.BACKEND_PORT}/notes",
            headers={"Telegram-ID": str(message.from_user.id)}) as response:

            if response.status == 200:
                notes = await response.json()
                for note in notes:
                    print(f"\n{note=}\n")
                    tags_list = list([tag['name'] for tag in note['tags']])
                    tags_str = ', '.join(tags_list) if tags_list else 'нет'
                    await message.answer(f"Заметка: {note['title']}\n"
                                         f"{note['content']}\n"
                                         f"Теги: {tags_str}")
            else:
                await message.answer("Ошибка при получении заметок.")


# Создание новой заметки (состояние FSM)
@router.message(Command("newnote"))
async def new_note_start(message: types.Message, state: FSMContext):
    await message.answer("Введите заголовок новой заметки.")
    await state.set_state(NoteForm.waiting_for_title)


@router.message(NoteForm.waiting_for_title)
async def note_title_received(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Теперь введите содержание заметки.")
    await state.set_state(NoteForm.waiting_for_content)


@router.message(NoteForm.waiting_for_content)
async def note_content_received(message: types.Message, state: FSMContext):
    await state.update_data(content=message.text)
    await message.answer(
        "Теперь введите теги для заметки (через запятую) или введите 'нет', если теги не нужны.")
    await state.set_state(NoteForm.waiting_for_tags)


@router.message(NoteForm.waiting_for_tags)
async def note_tags_received(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data['title']
    content = data['content']

    tags_input = message.text.strip()
    if tags_input.lower() == "нет":
        tags = []
    else:
        # Разбиваем строку на теги, убираем лишние пробелы
        tags = [tag.strip() for tag in tags_input.split(",")]

    async with aiohttp.ClientSession() as session:
        async with session.post(
                f"http://{s.BACKEND_HOST}:{s.BACKEND_PORT}/notes",
                json={"title": title, "content": content, "tags": tags},
                headers={"Telegram-ID": str(message.from_user.id)}) as response:

            print(f"Response status: {response.status}")
            print(f"Response text: {await response.text()}")  # Выводим тело ответа для отладки

            if response.status == 201:
                await message.answer("Заметка успешно создана!")
            else:
                await message.answer("Ошибка при создании заметки.")

    await state.clear()


# Поиск заметок по тегам
@router.message(Command("findnote"))
async def find_note_by_tag(message: types.Message):
    await message.answer("Введите тег для поиска заметок.")
    # Добавить логику поиска заметок по тегам
