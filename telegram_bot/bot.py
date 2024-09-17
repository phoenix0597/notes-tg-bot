import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from telegram_bot import handlers

from app.core.config import settings

TG_API_TOKEN = settings.TG_API_TOKEN  # API токен Telegram

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TG_API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрация хэндлеров
# register_handlers(dp)
dp.include_router(handlers.router)

# Настройка команд бота
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу"),
        BotCommand(command="/notes", description="Получить список заметок"),
        BotCommand(command="/newnote", description="Создать новую заметку"),
        BotCommand(command="/findnote", description="Найти заметку по тегу")
    ]
    await bot.set_my_commands(commands)

async def main():
    await set_bot_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
