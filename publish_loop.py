import argparse
import asyncio
import logging
import random
import os
from pathlib import Path
from typing import List, NoReturn

from dotenv import load_dotenv
from telegram import Bot
from telegram import error as telegram_error

from telegram_tools import publish_photo

logger = logging.getLogger(__name__)

def configure_logging() -> None:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

def get_telegram_token() -> str:
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN не найден в .env файле")
    return token

def get_telegram_channel() -> str:
    channel = os.getenv('TELEGRAM_CHANNEL')
    if not channel:
        raise RuntimeError("TELEGRAM_CHANNEL не найден в .env файле")
    return channel

def validate_directory(directory: Path) -> None:
    if not directory.exists():
        raise FileNotFoundError(f"Директория {directory} не существует")
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} не является директорией")
    if not os.access(directory, os.R_OK):
        raise PermissionError(f"Нет доступа к директории {directory}")

def get_image_files(directory: Path) -> List[Path]:
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    return [f for f in directory.iterdir()
           if f.is_file() and f.suffix.lower() in image_extensions]

async def validate_bot_access(bot: Bot, channel: str) -> None:
    await bot.get_chat(channel)

async def run_publishing_loop(bot: Bot, channel: str, directory: Path, interval: int) -> NoReturn:
    interval_seconds = interval * 3600
    logger.info(f"Запуск цикла публикации с интервалом {interval} часов")

    while True:
        images = get_image_files(directory)
        if not images:
            logger.warning(f"Нет изображений в директории {directory}")
            await asyncio.sleep(interval_seconds)
            continue

        random.shuffle(images)

        for photo_path in images:
            if await publish_photo(bot, channel, photo_path):
                logger.info(f"Опубликовано: {photo_path.name}")
                break
            logger.warning(f"Не удалось опубликовать: {photo_path.name}")

        await asyncio.sleep(interval_seconds)

async def async_main() -> None:
    parser = argparse.ArgumentParser(
        description='Публикация изображений в Telegram-канал'
    )
    parser.add_argument(
        '--directory',
        type=str,
        default='images',
        help='Директория с изображениями (по умолчанию: images)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=4,
        help='Интервал публикации в часах (по умолчанию: 4)'
    )
    args = parser.parse_args()

    directory = Path(args.directory)
    validate_directory(directory)

    bot = Bot(token=get_telegram_token())
    channel = get_telegram_channel()

    await validate_bot_access(bot, channel)

    logger.info(f"Бот запущен. Публикация каждые {args.interval} часов из {directory}")
    await run_publishing_loop(bot, channel, directory, args.interval)

def main() -> None:
    load_dotenv()
    configure_logging()
    asyncio.run(async_main())

if __name__ == "__main__":
    main()