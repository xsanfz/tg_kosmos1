from pathlib import Path
from typing import Optional
import os

from telegram import Bot
from telegram.error import TelegramError


def get_telegram_config():
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_channel = os.getenv('TELEGRAM_CHANNEL')
    return telegram_token, telegram_channel


async def publish_photo(bot: Bot, channel: str, photo_path: Path) -> bool:
    try:
        with open(photo_path, 'rb') as photo:
            await bot.send_photo(chat_id=channel, photo=photo)
        return True
    except TelegramError as e:
        print(f"Ошибка при публикации: {str(e)}")
        return False