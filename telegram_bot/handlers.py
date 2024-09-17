# telegram_bot/handlers.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from telegram_bot.auth import authorize_user
import aiohttp

from app.core.config import settings as s

router = Router()


# Определение состояний для FSM
class NoteForm(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()


# Обработчик команды /start
@router.message(Command("start"))
async def start(message: types.Message):
    user = await authorize_user(message.from_user.id)
    if user:
        await message.answer(f"Привет, {user['telegram_id']}! "
                             f"Вы авторизованы и можете получать список заметок, или создавать новые."
                             f"Для получения справки, как это работает, введите /help")
    else:
        # Если пользователь не найден, создаем его через регистрацию по telegram_id
        async with aiohttp.ClientSession() as session:
            # print(f"\n{message.from_user.id=}\n")
            # Отправляем запрос на регистрацию пользователя
            async with session.post(
                    # f"http://{s.BACKEND_HOST}:{s.BACKEND_PORT}/auth/register/telegram",
                    # json={"telegram_id": message.from_user.id}) as response:

                    f"http://{s.BACKEND_HOST}:{s.BACKEND_PORT}/auth/register/telegram",
                    headers={"Telegram-ID": str(message.from_user.id)}) as response:

                print(f"\n{response=}\n")
                print(f"{await response.text()=}")  # Выводим тело ответа для диагностики

                if response.status == 200:
                    await message.answer("Поздравляем, Вы зарегистрировались в приложении 'Мои заметки'! "
                                         "Для получения справки о работе с приложением введите /help")
                else:
                    await message.answer("Произошла ошибка при регистрации. Попробуйте снова позже.")


# Получение списка заметок
@router.message(Command("notes"))
async def get_notes(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://backend/notes") as response:
            if response.status == 200:
                notes = await response.json()
                for note in notes:
                    await message.answer(f"Заметка: {note['title']}\n{note['content']}")
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
    data = await state.get_data()
    title = data['title']
    content = message.text

    async with aiohttp.ClientSession() as session:
        async with session.post("http://backend/notes", json={"title": title, "content": content}) as response:
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

#
# def register_handlers(dp):
#     dp.include_router(router)
