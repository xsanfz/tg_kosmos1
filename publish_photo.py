import argparse
import random
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError


def get_telegram_token() -> Optional[str]:
    load_dotenv()
    return os.getenv('TELEGRAM_TOKEN')


def get_telegram_channel() -> Optional[str]:
    load_dotenv()
    return os.getenv('TELEGRAM_CHANNEL')


def get_random_image(directory: Path) -> Optional[Path]:
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    images = [f for f in directory.iterdir()
              if f.is_file() and f.suffix.lower() in image_extensions]
    return random.choice(images) if images else None


async def publish_single_photo(bot: Bot, channel: str, photo_path: Path) -> bool:
    try:
        with open(photo_path, 'rb') as photo:
            await bot.send_photo(chat_id=channel, photo=photo)
        print(f"Опубликовано: {photo_path.name}")
        return True
    except TelegramError as e:
        print(f"Ошибка при публикации: {str(e)}")
        return False


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

    telegram_token = get_telegram_token()
    telegram_channel = get_telegram_channel()

    if not telegram_token or not telegram_channel:
        print("Ошибка: Необходимо указать TELEGRAM_TOKEN и TELEGRAM_CHANNEL в .env файле")
        return

    bot = Bot(token=telegram_token)
    directory = Path(args.directory)

    if args.photo:
        photo_path = directory / args.photo
    else:
        photo_path = get_random_image(directory)

    if not photo_path or not photo_path.exists():
        print("Фото не найдено")
        return

    await publish_single_photo(bot, telegram_channel, photo_path)


def main():
    import asyncio
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
