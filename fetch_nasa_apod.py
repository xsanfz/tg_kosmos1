import argparse
import shutil
import requests
from space_utils import download_image, get_nasa_api_key, get_file_extension_from_url
from datetime import datetime


def fetch_apod_images(api_key, count=30):
    try:
        response = requests.get(
            'https://api.nasa.gov/planetary/apod',
            params={'api_key': api_key, 'count': count, 'thumbs': False},
            timeout=15
        )
        response.raise_for_status()
        return [item for item in response.json() if item.get('media_type') == 'image']
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return []


def main():
    parser = argparse.ArgumentParser(description='Скачать APOD фото NASA')
    parser.add_argument('--count', type=int, default=5, help='Количество фото (по умолчанию 5)')
    args = parser.parse_args()

    save_dir = "nasa_apod"
    shutil.rmtree(save_dir, ignore_errors=True)

    images = fetch_apod_images(get_nasa_api_key(), args.count)
    print(f"Найдено {len(images)} фото. Загрузка...")

    for i, item in enumerate(images, 1):
        url = item.get('hdurl') or item.get('url')
        ext = get_file_extension_from_url(url)
        filename = f"{save_dir}/apod_{i}{ext}"
        if download_image(url, filename):
            print(f"Сохранено: {filename}")


if __name__ == "__main__":
    main()