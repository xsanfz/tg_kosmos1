import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import requests
from requests.exceptions import RequestException, HTTPError, Timeout

from space_utils import download_image, get_nasa_api_key


def fetch_epic_images(api_key: str, count: int = 10) -> List[Dict]:
    try:
        response = requests.get(
            'https://api.nasa.gov/EPIC/api/natural/images',
            params={'api_key': api_key},
            timeout=15
        )
        response.raise_for_status()
        return response.json()[:count]

    except HTTPError as e:
        print(f"Ошибка NASA EPIC API: {e.response.status_code}")
        if e.response.status_code == 403:
            print("Проверьте правильность API ключа")
    except Timeout:
        print("Превышено время ожидания ответа от NASA EPIC API")
    except RequestException as e:
        print(f"Ошибка соединения: {str(e)}")
    except ValueError as e:
        print(f"Ошибка обработки данных: {str(e)}")

    return []


def generate_epic_url(api_key: str, image_data: Dict) -> Optional[str]:
    try:
        date = datetime.strptime(image_data['date'], "%Y-%m-%d %H:%M:%S")
        return (
            f"https://api.nasa.gov/EPIC/archive/natural/"
            f"{date:%Y/%m/%d}/png/{image_data['image']}.png"
            f"?api_key={api_key}"
        )
    except (KeyError, ValueError) as e:
        print(f"Ошибка генерации URL: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Скачать EPIC (Earth Polychromatic Imaging Camera) изображения Земли от NASA',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='Количество изображений для загрузки (макс. 10)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='nasa_epic',
        help='Папка для сохранения изображений'
    )
    args = parser.parse_args()

    api_key = get_nasa_api_key()
    if not api_key:
        print("NASA API ключ не найден. Проверьте .env файл")
        return

    images = fetch_epic_images(api_key, min(args.count, 10))
    if not images:
        print("Не найдено доступных EPIC изображений")
        return

    save_dir = Path(args.output)
    shutil.rmtree(save_dir, ignore_errors=True)
    save_dir.mkdir(parents=True, exist_ok=True)

    print(f"Найдено {len(images)} изображений. Начинаю загрузку...")

    success_count = 0
    for i, img_data in enumerate(images, 1):
        url = generate_epic_url(api_key, img_data)
        if not url:
            continue

        filename = save_dir / f"epic_{i}_{img_data['image']}.png"
        if download_image(url, str(filename)):
            success_count += 1
            print(f"Успешно: {filename.name}")

    print(f"\nЗавершено. Успешно загружено {success_count} из {len(images)} изображений")


if __name__ == "__main__":
    main()
