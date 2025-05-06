import argparse
import shutil
import requests
from space_utils import download_image, get_nasa_api_key
from datetime import datetime


def fetch_epic_images(api_key, count=10):
    try:
        response = requests.get(
            f'https://api.nasa.gov/EPIC/api/natural/images?api_key={api_key}',
            timeout=10
        )
        response.raise_for_status()
        return response.json()[:count]
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return []


def get_epic_url(api_key, image_data):
    date = datetime.strptime(image_data['date'], "%Y-%m-%d %H:%M:%S")
    return (
        f"https://api.nasa.gov/EPIC/archive/natural/"
        f"{date:%Y/%m/%d}/png/{image_data['image']}.png?api_key={api_key}"
    )


def main():
    parser = argparse.ArgumentParser(description='Скачать EPIC фото Земли')
    parser.add_argument('--count', type=int, default=5, help='Количество фото (по умолчанию 5)')
    args = parser.parse_args()

    save_dir = "nasa_epic"
    shutil.rmtree(save_dir, ignore_errors=True)

    images = fetch_epic_images(get_nasa_api_key(), args.count)
    print(f"Найдено {len(images)} фото. Загрузка...")

    for i, img in enumerate(images, 1):
        url = get_epic_url(get_nasa_api_key(), img)
        filename = f"{save_dir}/epic_{i}.png"
        if download_image(url, filename):
            print(f"Сохранено: {filename}")


if __name__ == "__main__":
    main()