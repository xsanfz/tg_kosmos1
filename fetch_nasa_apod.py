import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import requests
from requests.exceptions import RequestException, HTTPError, Timeout

from space_utils import download_image, get_nasa_api_key, get_file_extension_from_url
from error_handlers import (
    handle_nasa_api_error,
    handle_data_format_error,
    handle_download_error,
    handle_config_error,
    handle_connection_error
)


def fetch_apod_images(api_key: str, image_count: int = 30) -> Optional[List[Dict]]:
    try:
        response = requests.get(
            'https://api.nasa.gov/planetary/apod',
            params={
                'api_key': api_key,
                'count': image_count,
                'thumbs': True
            },
            timeout=15
        )
        response.raise_for_status()

        apod_entries = response.json()
        if not isinstance(apod_entries, list):
            handle_data_format_error("NASA API вернул неожиданный формат данных - ожидался список")
            return None

        return [item for item in apod_entries if item.get('media_type') == 'image']
    except HTTPError as error:
        handle_nasa_api_error(f"{error.response.status_code}")
        return None
    except Timeout:
        handle_connection_error("Превышено время ожидания ответа от NASA API")
        return None
    except RequestException as error:
        handle_connection_error(str(error))
        return None


def create_apod_filename(
        output_dir: Path,
        apod_date: str,
        image_url: str,
        fallback_index: int
) -> Optional[Path]:
    try:
        publication_date = datetime.strptime(apod_date, '%Y-%m-%d')
        date_prefix = publication_date.strftime('%Y%m%d')
    except ValueError:
        date_prefix = f"no_date_{fallback_index}"

    if not image_url:
        handle_data_format_error("Невозможно создать имя файла - отсутствует URL изображения")
        return None

    file_extension = get_file_extension_from_url(image_url)
    return output_dir / f"apod_{date_prefix}{file_extension}"


def main():
    parser = argparse.ArgumentParser(
        description='Download Astronomy Picture of Day (APOD) from NASA',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='Number of images to download (max 30)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='nasa_apod',
        help='Directory to save downloaded images'
    )
    args = parser.parse_args()

    api_key = get_nasa_api_key()
    if not api_key:
        return

    apod_images = fetch_apod_images(api_key, min(args.count, 30))
    if not apod_images:
        return

    try:
        output_dir = Path(args.output)
        shutil.rmtree(output_dir, ignore_errors=True)
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        handle_nasa_api_error(f"Не удалось подготовить выходную директорию {args.output}: {error}")
        return

    print(f"Найдено {len(apod_images)} изображений. Начинаем загрузку...")

    success_count = 0
    for index, apod_entry in enumerate(apod_images, 1):
        image_url = apod_entry.get('hdurl') or apod_entry.get('url')
        if not image_url:
            print(f"Пропускаем элемент {index}: URL изображения не найден")
            continue

        output_path = create_apod_filename(
            output_dir=output_dir,
            apod_date=apod_entry.get('date', ''),
            image_url=image_url,
            fallback_index=index
        )
        if not output_path:
            continue

        try:
            download_result = download_image(image_url, str(output_path))
        except (RequestException, OSError, RuntimeError) as error:
            print(f"Ошибка при загрузке элемента {index}: {str(error)}")
            continue

        if download_result:
            success_count += 1
            print(f"Загружено: {output_path.name}")

    print(f"\nЗавершено. Успешно загружено {success_count} из {len(apod_images)} изображений")


if __name__ == "__main__":
    main()