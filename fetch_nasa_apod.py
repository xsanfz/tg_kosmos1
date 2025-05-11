import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import requests
from requests.exceptions import RequestException, HTTPError, Timeout

from space_utils import download_image, get_nasa_api_key, get_file_extension_from_url


def fetch_apod_images(api_key: str, count: int = 30) -> List[Dict]:
    try:
        response = requests.get(
            'https://api.nasa.gov/planetary/apod',
            params={
                'api_key': api_key,
                'count': count,
                'thumbs': False
            },
            timeout=15
        )
        response.raise_for_status()

        return [
            item for item in response.json()
            if item.get('media_type') == 'image'
        ]

    except HTTPError as e:
        print(f"Ошибка NASA API: {e.response.status_code}")
        if e.response.status_code == 403:
            print("Проверьте правильность API ключа")
    except Timeout:
        print("Превышено время ожидания ответа от NASA API")
    except RequestException as e:
        print(f"Ошибка соединения: {str(e)}")
    except ValueError as e:
        print(f"Ошибка обработки данных: {str(e)}")

    return []


def create_unique_filename(save_dir: Path, item: Dict, index: int) -> Path:
    date_str = item.get('date', '')
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_part = date_obj.strftime('%Y%m%d')
    except (ValueError, TypeError):
        date_part = f"unknown_{index}"

    url = item.get('hdurl') or item.get('url')
    ext = get_file_extension_from_url(url)
    return save_dir / f"apod_{date_part}{ext}"


def main():
    parser = argparse.ArgumentParser(
        description='Скачать Astronomy Picture of Day (APOD) от NASA',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='Количество изображений для загрузки (макс. 30)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='nasa_apod',
        help='Папка для сохранения изображений'
    )
    args = parser.parse_args()

    api_key = get_nasa_api_key()
    if not api_key:
        print("NASA API ключ не найден. Проверьте .env файл")
        return

    images = fetch_apod_images(api_key, min(args.count, 30))
    if not images:
        print("Не найдено подходящих изображений")
        return

    save_dir = Path(args.output)
    shutil.rmtree(save_dir, ignore_errors=True)
    save_dir.mkdir(parents=True, exist_ok=True)

    print(f"Найдено {len(images)} изображений. Начинаю загрузку...")

    success_count = 0
    for i, item in enumerate(images, 1):
        url = item.get('hdurl') or item.get('url')
        if not url:
            continue

        filename = create_unique_filename(save_dir, item, i)
        if download_image(url, str(filename)):
            success_count += 1
            print(f"Успешно: {filename.name}")

    print(f"\nЗавершено. Успешно загружено {success_count} из {len(images)} изображений")


if __name__ == "__main__":
    main()
