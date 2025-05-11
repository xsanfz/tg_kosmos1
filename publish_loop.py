import argparse
import asyncio
import random
import time
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError


def get_telegram_token() -> str:
    load_dotenv()
    return os.getenv('TELEGRAM_TOKEN')


def get_telegram_channel() -> str:
    load_dotenv()
    return os.getenv('TELEGRAM_CHANNEL')


def get_image_files(directory: Path) -> List[Path]:
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    return [f for f in directory.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions]


async def publish_photo(bot: Bot, channel: str, photo_path: Path) -> bool:
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
        description='Публикация изображений в Telegram-канал в бесконечном цикле'
    )
    parser.add_argument(
        '--directory',
        type=str,
        default='images',
        help='Директория с изображениями'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=4,
        help='Интервал публикации в часах'
    )
    args = parser.parse_args()

    telegram_token = get_telegram_token()
    telegram_channel = get_telegram_channel()

    if not telegram_token or not telegram_channel:
        print("Ошибка: Необходимо указать TELEGRAM_TOKEN и TELEGRAM_CHANNEL в .env файле")
        return

    bot = Bot(token=telegram_token)
    directory = Path(args.directory)
    interval_seconds = args.interval * 3600

    print(f"Бот запущен. Публикация каждые {args.interval} часов из {directory}")

    while True:
        try:
            images = get_image_files(directory)
            if not images:
                print(f"В директории {directory} нет изображений")
                await asyncio.sleep(interval_seconds)
                continue

            random.shuffle(images)
            for photo_path in images:
                if await publish_photo(bot, telegram_channel, photo_path):
                    break

            await asyncio.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nБот остановлен")
            break
        except Exception as e:
            print(f"Ошибка: {str(e)}")
            await asyncio.sleep(60)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
