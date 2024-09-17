# telegram_bot/auth.py
import aiohttp
from app.core.config import settings as s


async def authorize_user(telegram_user_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{s.BACKEND_HOST}/auth/telegram/{telegram_user_id}") as response:
            if response.status == 200:
                response_json = await response.json()
                return response_json
            else:
                return None
