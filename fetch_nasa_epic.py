import argparse
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime

import requests
from requests.exceptions import RequestException


def get_nasa_api_key() -> str:
    import os
    api_key = os.getenv('NASA_API_KEY')
    if not api_key:
        raise ValueError(
            "NASA API ключ не найден. Установите переменную окружения NASA_API_KEY "
            "или измените код для его запроса."
        )
    return api_key


def download_image(url: str, params: Dict, filepath: str) -> None:
    response = requests.get(url, params=params, stream=True, timeout=15)
    response.raise_for_status()

    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def fetch_epic_images(api_key: str, count: int = 10) -> List[Dict]:
    base_url = 'https://api.nasa.gov/EPIC/api/natural/images'
    response = requests.get(
        base_url,
        params={'api_key': api_key},
        timeout=15
    )
    response.raise_for_status()
    images = response.json()
    return images[:min(count, len(images))]


def generate_epic_base_url(image_data: Dict) -> str:
    date = datetime.strptime(image_data['date'], "%Y-%m-%d %H:%M:%S")
    return (
        f"https://api.nasa.gov/EPIC/archive/natural/"
        f"{date:%Y/%m/%d}/png/{image_data['image']}.png"
    )


def main():
    parser = argparse.ArgumentParser(
        description='Скачивание изображений Земли NASA EPIC',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='Количество изображений для скачивания (максимум 10)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='nasa_epic',
        help='Директория для сохранения изображений'
    )
    args = parser.parse_args()

    try:
        api_key = get_nasa_api_key()
        save_dir = Path(args.output)
        shutil.rmtree(save_dir, ignore_errors=True)
        save_dir.mkdir(parents=True, exist_ok=True)

        images = fetch_epic_images(api_key, min(args.count, 10))
        print(f"Найдено {len(images)} изображений. Скачивание...")

        success_count = 0
        for i, img_data in enumerate(images, 1):
            try:
                base_url = generate_epic_base_url(img_data)
                filename = save_dir / f"epic_{i}_{img_data['image']}.png"

                download_image(base_url, {'api_key': api_key}, str(filename))
                success_count += 1
                print(f"Скачано: {filename.name}")
            except (KeyError, ValueError) as e:
                print(f"Пропуск изображения {i}: Неверные метаданные - {str(e)}")
            except (RequestException, OSError) as e:
                print(f"Ошибка скачивания изображения {i}: {str(e)}")

        print(f"\nГотово. Успешно скачано {success_count}/{len(images)} изображений")

    except ValueError as e:
        print(f"Ошибка конфигурации: {str(e)}")
    except RequestException as e:
        print(f"Ошибка запроса к NASA API: {str(e)}")
    except OSError as e:
        print(f"Ошибка файловой системы: {str(e)}")


if __name__ == "__main__":
    main()