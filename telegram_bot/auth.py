# telegram_bot/auth.py
import aiohttp
from app.core.config import settings as s


async def authorize_user(telegram_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f"http://{s.BACKEND_HOST}:{s.BACKEND_PORT}/auth/login/telegram",
                headers={"Telegram-ID": str(telegram_id)}) as response:

            if response.status == 200:
                # Пользователь найден, возвращаем данные
                user_data = await response.json()
                return user_data
            else:
                # Пользователь не найден
                return None
