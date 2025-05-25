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

def get_telegram_token() -> str:
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logger.error("Токен Telegram не найден в .env файле")
        raise RuntimeError("TELEGRAM_TOKEN не найден в .env файле")
    logger.debug("Токен Telegram успешно получен")
    return token

def get_telegram_channel() -> str:
    channel = os.getenv('TELEGRAM_CHANNEL')
    if not channel:
        logger.error("ID канала не найден в .env файле")
        raise RuntimeError("TELEGRAM_CHANNEL не найден в .env файле")
    logger.debug(f"ID канала получен: {channel}")
    return channel

def validate_directory(directory: Path) -> None:
    if not directory.exists():
        logger.error(f"Директория {directory} не существует")
        raise FileNotFoundError(f"Директория {directory} не существует")
    if not directory.is_dir():
        logger.error(f"{directory} не является директорией")
        raise NotADirectoryError(f"{directory} не является директорией")
    if not os.access(directory, os.R_OK):
        logger.error(f"Нет доступа к директории {directory}")
        raise PermissionError(f"Нет доступа к директории {directory}")
    logger.debug(f"Директория {directory} проверена и доступна")

def get_image_files(directory: Path) -> List[Path]:
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    try:
        files = [f for f in directory.iterdir()
                if f.is_file() and f.suffix.lower() in image_extensions]
        logger.info(f"Найдено {len(files)} изображений в директории {directory}")
        return files
    except OSError as e:
        logger.error(f"Ошибка доступа к директории: {e}")
        return []

async def validate_bot_access(bot: Bot, channel: str) -> None:
    try:
        await bot.get_chat(channel)
        logger.info(f"Бот успешно подключен к каналу {channel}")
    except telegram_error.Unauthorized as e:
        logger.error("Неверный токен бота", exc_info=True)
        raise RuntimeError("Неверный токен бота") from e
    except telegram_error.BadRequest as e:
        logger.error(f"Канал {channel} не найден или бот не имеет доступа", exc_info=True)
        raise RuntimeError(f"Канал {channel} не найден или бот не имеет доступа") from e

async def run_publishing_loop(bot: Bot, channel: str, directory: Path, interval: int) -> NoReturn:
    interval_seconds = interval * 3600
    logger.info(f"Запуск цикла публикации с интервалом {interval} часов")

    while True:
        images = get_image_files(directory)
        if not images:
            logger.warning(f"В директории {directory} нет изображений. Повторная проверка через {interval} часов")
            await asyncio.sleep(interval_seconds)
            continue

        random.shuffle(images)
        logger.debug(f"Список изображений для публикации перемешан ({len(images)} шт.)")

        for photo_path in images:
            try:
                success = await publish_photo(bot, channel, photo_path)
                if success:
                    logger.info(f"Успешно опубликовано изображение: {photo_path.name}")
                    break
                logger.warning(f"Не удалось опубликовать изображение: {photo_path.name}")
            except Exception as e:
                logger.error(f"Ошибка при публикации изображения {photo_path.name}: {str(e)}", exc_info=True)

        logger.info(f"Ожидание следующей публикации через {interval} часов")
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

    try:
        await run_publishing_loop(bot, channel, directory, args.interval)
    except KeyboardInterrupt:
        logger.info("Работа бота остановлена пользователем")
    except asyncio.CancelledError:
        logger.info("Задачи бота были отменены")
    except SystemExit:
        logger.info("Получен сигнал SystemExit")
        raise
    except BaseException as e:
        logger.critical(f"Критическая ошибка в основном цикле: {e}", exc_info=True)
        raise

def configure_logging() -> None:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger.info("Логирование сконфигурировано")

def main() -> None:
    load_dotenv()
    configure_logging()  # Конфигурируем логгер здесь

    try:
        asyncio.run(async_main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Приложение завершено")
    except SystemExit:
        logger.info("Завершение работы по SystemExit")
        raise
    except BaseException as e:
        logger.critical(f"Фатальная ошибка: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()