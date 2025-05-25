import argparse
import asyncio
import logging
import random
import os
import sys
from contextlib import suppress
from pathlib import Path
from typing import NoReturn

from dotenv import load_dotenv
from telegram import Bot
from telegram import error as telegram_error

from telegram_tools import publish_photo
from image_utils import get_image_files

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )


def get_telegram_bot_token() -> str:
    bot_token = os.getenv('TELEGRAM_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_TOKEN not found in .env file")
        sys.exit(1)
    return bot_token


def get_telegram_channel_id() -> str:
    channel_id = os.getenv('TELEGRAM_CHANNEL')
    if not channel_id:
        logger.error("TELEGRAM_CHANNEL not found in .env file")
        sys.exit(1)
    return channel_id


def validate_image_directory(image_directory: Path) -> None:
    if not image_directory.exists():
        logger.error(f"Directory {image_directory} does not exist")
        sys.exit(1)
    if not image_directory.is_dir():
        logger.error(f"{image_directory} is not a directory")
        sys.exit(1)
    if not os.access(image_directory, os.R_OK):
        logger.error(f"No read access to directory {image_directory}")
        sys.exit(1)


async def verify_bot_has_channel_access(bot: Bot, channel_id: str) -> None:
    try:
        await bot.get_chat(channel_id)
    except telegram_error.Unauthorized as error:
        logger.error("Invalid bot token")
        sys.exit(1)
    except telegram_error.BadRequest as error:
        logger.error(f"Channel {channel_id} not found or bot has no access")
        sys.exit(1)


async def publish_images_periodically(
        bot: Bot,
        channel_id: str,
        image_directory: Path,
        hours_interval: int
) -> NoReturn:
    interval_seconds = hours_interval * 3600
    logger.info(f"Starting publication loop with {hours_interval} hour interval")

    with suppress(KeyboardInterrupt, asyncio.CancelledError):
        while True:
            image_files = get_image_files(image_directory)
            if not image_files:
                logger.warning(f"No images found in directory {image_directory}")
                await asyncio.sleep(interval_seconds)
                continue

            random.shuffle(image_files)

            for image_path in image_files:
                if await publish_photo(bot, channel_id, image_path):
                    logger.info(f"Published: {image_path.name}")
                    break
                logger.warning(f"Failed to publish: {image_path.name}")

            await asyncio.sleep(interval_seconds)


async def async_main() -> None:
    parser = argparse.ArgumentParser(
        description='Publish images to Telegram channel'
    )
    parser.add_argument(
        '--directory',
        type=str,
        default='images',
        help='Directory with images (default: images)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=4,
        help='Publication interval in hours (default: 4)'
    )
    args = parser.parse_args()

    image_directory = Path(args.directory)
    validate_image_directory(image_directory)

    bot = Bot(token=get_telegram_bot_token())
    channel_id = get_telegram_channel_id()

    await verify_bot_has_channel_access(bot, channel_id)

    logger.info(f"Bot started. Publishing every {args.interval} hours from {image_directory}")
    await publish_images_periodically(bot, channel_id, image_directory, args.interval)


def main() -> None:
    load_dotenv()
    configure_logging()
    asyncio.run(async_main())


if __name__ == "__main__":
    main()