import argparse
import asyncio
import os
import random
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from telegram import Bot

from telegram_tools import get_telegram_config, publish_photo


def find_image(directory: Path, photo_name: Optional[str] = None) -> Optional[Path]:
    if photo_name:
        image_path = directory / photo_name
        return image_path if image_path.exists() else None

    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    images = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    return random.choice(images) if images else None


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
    photo_path = find_image(directory, args.photo)
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