import argparse
import logging
import random
import sys
from pathlib import Path

from telegram import Bot
from telegram import error as telegram_error

from telegram_tools import publish_photo
from image_tools import get_image_files
from env_utils import get_env_variable

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Publish photo to Telegram channel')
    parser.add_argument('--photo', type=str, help='Specific photo to publish')
    args = parser.parse_args()

    directory = Path("images")
    images = get_image_files(directory)
    if not images:
        logger.error("No images found in directory")
        sys.exit(1)

    photo_path = get_image_files(directory, args.photo) if args.photo else random.choice(images)
    if not photo_path:
        logger.error("Photo not found")
        sys.exit(1)

    bot = Bot(token=get_env_variable('TELEGRAM_TOKEN'))
    channel_id = get_env_variable('TELEGRAM_CHANNEL')

    try:
        bot.send_photo(chat_id=channel_id, photo=open(photo_path, 'rb'))
        logger.info(f"Published: {photo_path.name}")
    except telegram_error.TelegramError as e:
        logger.error(f"Failed to publish photo: {e}")
        sys.exit(1)
    except OSError as e:
        logger.error(f"Failed to read image file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()