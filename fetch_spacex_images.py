import argparse
import shutil
from pathlib import Path
from typing import List, Optional

import requests
from requests.exceptions import RequestException, HTTPError
from space_utils import get_file_extension_from_url
from error_handlers import (
    handle_spacex_api_error,
    handle_data_format_error,
    handle_download_error,
    handle_connection_error
)


def fetch_spacex_launch_image_urls(launch_id: str = 'latest') -> Optional[List[str]]:
    api_base_url = 'https://api.spacexdata.com/v4/launches/'
    launch_api_url = f'{api_base_url}{launch_id}'

    try:
        response = requests.get(launch_api_url, timeout=10)
        response.raise_for_status()

        launch_details = response.json()

        flickr_photos = launch_details.get('links', {}).get('flickr', {})
        image_urls = flickr_photos.get('original', [])

        if not isinstance(image_urls, list):
            handle_data_format_error("Данные изображений не являются списком")
            return None

        return image_urls
    except HTTPError as error:
        handle_spacex_api_error(f"{error.response.status_code}")
        return None
    except RequestException as error:
        handle_connection_error(str(error))
        return None


def download_image(image_url: str, save_path: str) -> bool:
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()
    except RequestException as e:
        handle_download_error(f"Не удалось загрузить изображение: {e}")
        return False

    try:
        with open(save_path, 'wb') as output_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, output_file)
        return True
    except OSError as e:
        handle_download_error(f"Не удалось сохранить изображение: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Download SpaceX launch photos',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--launch-id',
        help='Specific launch ID (default: latest launch)',
        default='latest'
    )
    parser.add_argument(
        '--output-dir',
        help='Directory to save downloaded images',
        default='spacex_images'
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    try:
        shutil.rmtree(output_dir, ignore_errors=True)
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        handle_spacex_api_error(f"Не удалось создать выходную директорию: {e}")
        return

    flickr_image_urls = fetch_spacex_launch_image_urls(args.launch_id)
    if not flickr_image_urls:
        return

    print(f"Найдено {len(flickr_image_urls)} изображений. Загружаем...")

    success_count = 0
    for idx, image_url in enumerate(flickr_image_urls, start=1):
        file_extension = get_file_extension_from_url(image_url)
        image_filename = output_dir / f"spacex_{idx}{file_extension}"

        try:
            download_result = download_image(image_url, str(image_filename))
        except (RequestException, OSError, RuntimeError) as e:
            print(f"Ошибка при загрузке изображения {idx}: {e}")
            continue

        if download_result:
            success_count += 1
            print(f"Загружено: {image_filename.name}")

    print(f"\nРезультаты: {success_count} успешно, {len(flickr_image_urls) - success_count} не удалось")


if __name__ == "__main__":
    main()