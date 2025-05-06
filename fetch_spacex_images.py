import argparse
import shutil
import requests
from space_utils import download_image, get_file_extension_from_url


def get_spacex_launch_images(launch_id=None):
    url = 'https://api.spacexdata.com/v4/launches/latest' if launch_id is None \
        else f'https://api.spacexdata.com/v4/launches/{launch_id}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        images = response.json()['links']['flickr']['original']
        return images if images else []
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return []


def main():
    parser = argparse.ArgumentParser(description='Скачать фото запуска SpaceX')
    parser.add_argument('--id', help='ID запуска (если не указан - последний)')
    args = parser.parse_args()

    images = get_spacex_launch_images(args.id)
    if not images:
        print("Фото не найдены")
        return

    save_dir = "spacex_images"
    shutil.rmtree(save_dir, ignore_errors=True)

    print(f"Найдено {len(images)} фото. Загрузка...")
    for i, url in enumerate(images, 1):
        filename = f"{save_dir}/spacex_{i}{get_file_extension_from_url(url)}"
        if download_image(url, filename):
            print(f"Сохранено: {filename}")


if __name__ == "__main__":
    main()