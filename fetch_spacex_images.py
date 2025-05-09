import argparse
import shutil
from pathlib import Path
from typing import List, Optional

import requests
from requests.exceptions import RequestException, HTTPError, Timeout

from space_utils import download_image, get_file_extension_from_url


def get_spacex_launch_images(launch_id: Optional[str] = None) -> List[str]:
    base_url = 'https://api.spacexdata.com/v4/launches/'
    url = f'{base_url}latest' if launch_id is None else f'{base_url}{launch_id}'

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get('links', {}).get('flickr', {}).get('original'):
            return []

        return data['links']['flickr']['original']

    except HTTPError as e:
        print(f"Ошибка API: {e.response.status_code} - {e.response.text}")
    except Timeout:
        print("Превышено время ожидания ответа от API SpaceX")
    except RequestException as e:
        print(f"Ошибка соединения: {str(e)}")
    except (KeyError, ValueError) as e:
        print(f"Ошибка обработки данных: {str(e)}")

    return []


def main():
    parser = argparse.ArgumentParser(
        description='Скачать фотографии запуска SpaceX',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--id',
        help='ID конкретного запуска (если не указан - последний)',
        default=None
    )
    parser.add_argument(
        '--output',
        help='Папка для сохранения изображений',
        default='spacex_images'
    )
    args = parser.parse_args()

    images = get_spacex_launch_images(args.id)
    if not images:
        print("Не найдено изображений для данного запуска")
        return

    save_dir = Path(args.output)
    shutil.rmtree(save_dir, ignore_errors=True)
    save_dir.mkdir(parents=True, exist_ok=True)

    print(f"Найдено {len(images)} изображений. Начинаю загрузку...")

    success_count = 0
    for i, url in enumerate(images, 1):
        filename = save_dir / f"spacex_{i}{get_file_extension_from_url(url)}"
        if download_image(url, str(filename)):
            success_count += 1
            print(f"Успешно: {filename}")

    print(f"\nЗавершено. Успешно загружено {success_count} из {len(images)} изображений")


if __name__ == "__main__":
    main()