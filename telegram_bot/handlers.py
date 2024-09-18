# telegram_bot/handlers.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import aiohttp
from typer.cli import state

from app.core.config import settings as s
from telegram_bot.auth import authorize_user

router = Router()


# Определение состояний для FSM
class NoteForm(StatesGroup):
    waiting_for_title = State()  # состояние для ввода заголовка заметки
    waiting_for_content = State()  # состояние для ввода содержания заметки
    waiting_for_tags = State()  # состояние для ввода тегов к заметке
    searching_by_tags = State()  # состояние для поиска заметок по тегам


# Обработчик команды /start
@router.message(Command("start"))
async def start(message: types.Message):
    user = await authorize_user(message.from_user.id)

    print(f"\n{user=}\n")
    if user:
        # Пользователь найден, авторизован
        await message.answer(f"Привет, {user['telegram_id']}!\n"
                             f"Вы авторизованы и можете получать список заметок, или создавать новые."
                             f"Команды по работе с заметками доступны в 'Меню'.")
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
                                         "Команды по работе с заметками доступны в 'Меню'.")
                else:
                    await message.answer("Произошла ошибка при регистрации. Попробуйте снова позже.")


# Вспомогательная функция для отображения списка заметок
async def display_notes(notes: list, message: types.Message):
    """Отображение списка заметок в сообщениях Telegram."""
    for note in notes:
        tags_list = [tag['name'] for tag in note['tags']]
        tags_str = ', '.join(tags_list) if tags_list else 'нет'
        await message.answer(
            f"Заметка: {note['title']}\n"
            f"{note['content']}\n"
            f"Теги: {tags_str}"
        )


# Получение списка заметок
@router.message(Command("notes"))
async def get_notes(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{s.BACKEND_HOST}:{s.BACKEND_PORT}/notes",
                               headers={"Telegram-ID": str(message.from_user.id)}) as response:

            if response.status == 200:
                notes = await response.json()
                if notes:
                    await display_notes(notes, message)  # Используем вспомогательную функцию
                else:
                    await message.answer("У вас нет заметок.")
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
async def find_note_by_tag(message: types.Message, state: FSMContext):
    await message.answer("Введите теги для поиска (через запятую).")
    await state.set_state(NoteForm.searching_by_tags)


# Обработчик для ввода тегов
@router.message(NoteForm.searching_by_tags)
async def handle_tags_input(message: types.Message, state: FSMContext):
    tags_input = message.text.strip()
    tags = [tag.strip() for tag in tags_input.split(",")]  # Разбиваем строку на теги

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://{s.BACKEND_HOST}:{s.BACKEND_PORT}/notes/search",
            params={"tags": tags},  # Передаем теги в параметрах запроса
            headers={"Telegram-ID": str(message.from_user.id)}
        ) as response:
            if response.status == 200:
                notes = await response.json()
                if notes:
                    await display_notes(notes, message)  # Используем вспомогательную функцию
                else:
                    await message.answer("Заметки с такими тегами не найдены.")
            else:
                await message.answer("Ошибка при поиске заметок.")

    # Завершаем состояние после поиска
    await state.clear()