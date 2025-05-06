import os
import requests
from pathlib import Path
import shutil


def download_image(image_url: str, save_path: str) -> bool:

    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        folder = os.path.dirname(save_path)
        Path(folder).mkdir(parents=True, exist_ok=True)

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return True

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании {image_url}: {e}")
        return False


def main():

    images_dir = "images"
    if os.path.exists(images_dir):
        shutil.rmtree(images_dir)

    hubble_url = "https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg"
    save_path = os.path.join(images_dir, "hubble.jpg")

    if download_image(hubble_url, save_path):
        print(f"Успешно загружено: {save_path}")
    else:
        print(f"Не удалось загрузить: {hubble_url}")


if __name__ == "__main__":
    main()