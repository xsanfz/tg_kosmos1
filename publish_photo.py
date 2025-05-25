import argparse
import asyncio
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from telegram import Bot

from telegram_tools import get_telegram_config, publish_photo
from image_utils import get_image_files, get_random_image


async def main_async():
    parser = argparse.ArgumentParser(
        description='Публикация фотографии в Telegram-канал'
    )
    parser.add_argument(
        '--directory',
        type=str,
        default='images',
        help='Директория с изображениями'
    )
    parser.add_argument(
        '--photo',
        type=str,
        help='Конкретное фото для публикации (если не указано - случайное)'
    )
    args = parser.parse_args()

    telegram_token, telegram_channel = get_telegram_config()
    if not telegram_token or not telegram_channel:
        raise ValueError("Необходимо указать TELEGRAM_TOKEN и TELEGRAM_CHANNEL в .env файле")

    directory = Path(args.directory)
    photo_path = get_image_files(directory, args.photo) if args.photo else get_random_image(directory)
    if not photo_path:
        raise FileNotFoundError(f"Изображение не найдено в директории {directory}")

    bot = Bot(token=telegram_token)
    success = await publish_photo(bot, telegram_channel, photo_path)
    if success:
        print(f"Успешно опубликовано: {photo_path.name}")


def main():
    load_dotenv()

    try:
        asyncio.run(main_async())
    except ValueError as e:
        print(f"Ошибка конфигурации: {str(e)}")
    except FileNotFoundError as e:
        print(f"Ошибка поиска изображения: {str(e)}")


if __name__ == "__main__":
    main()