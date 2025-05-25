import argparse
import asyncio
import logging
import random
import os
from contextlib import suppress
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
        logger.error("TELEGRAM_TOKEN не найден в .env файле")
        raise SystemExit(1)
    return token


def get_telegram_channel() -> str:
    channel = os.getenv('TELEGRAM_CHANNEL')
    if not channel:
        logger.error("TELEGRAM_CHANNEL не найден в .env файле")
        raise SystemExit(1)
    return channel


def validate_directory(directory: Path) -> None:
    if not directory.exists():
        logger.error(f"Директория {directory} не существует")
        raise SystemExit(1)
    if not directory.is_dir():
        logger.error(f"{directory} не является директорией")
        raise SystemExit(1)
    if not os.access(directory, os.R_OK):
        logger.error(f"Нет доступа к директории {directory}")
        raise SystemExit(1)


def get_image_files(directory: Path) -> List[Path]:
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    return [f for f in directory.iterdir()
           if f.is_file() and f.suffix.lower() in image_extensions]


async def validate_bot_access(bot: Bot, channel: str) -> None:
    try:
        await bot.get_chat(channel)
    except telegram_error.Unauthorized:
        logger.error("Неверный токен бота")
        raise SystemExit(1)
    except telegram_error.BadRequest:
        logger.error(f"Канал {channel} не найден или бот не имеет доступа")
        raise SystemExit(1)


async def run_publishing_loop(bot: Bot, channel: str, directory: Path, interval: int) -> NoReturn:
    interval_seconds = interval * 3600
    logger.info(f"Запуск цикла публикации с интервалом {interval} часов")

    with suppress(KeyboardInterrupt, asyncio.CancelledError):
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