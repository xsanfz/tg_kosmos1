from pathlib import Path
from typing import Optional

from telegram import Bot
from telegram.error import TelegramError


async def publish_photo(bot: Bot, channel: str, photo_path: Path) -> bool:
    try:
        with open(photo_path, 'rb') as photo:
            await bot.send_photo(chat_id=channel, photo=photo)
        return True
    except TelegramError as e:
        print(f"Ошибка при публикации: {str(e)}")
        return False