import os
import logging
from pathlib import Path
from typing import Optional, Tuple

from telegram import Bot
from telegram import error as telegram_error

from env_utils import get_env_variable

logger = logging.getLogger(__name__)


def get_telegram_config() -> Tuple[str, str]:
    telegram_token = get_env_variable('TELEGRAM_TOKEN')
    telegram_channel = get_env_variable('TELEGRAM_CHANNEL')
    return telegram_token, telegram_channel


async def publish_photo(bot: Bot, channel_id: str, image_path: Path) -> None:
    with open(image_path, 'rb') as photo:
        await bot.send_photo(chat_id=channel_id, photo=photo)