import os
import requests
from pathlib import Path
import shutil
from urllib.parse import urlsplit, unquote
from dotenv import load_dotenv


def get_file_extension_from_url(url):
    parsed = urlsplit(url)
    path = unquote(parsed.path)
    filename = os.path.split(path)[1]
    _, ext = os.path.splitext(filename)
    return ext.lower() if ext else '.jpg'


def download_image(image_url, save_path):
    try:
        response = requests.get(image_url, stream=True, timeout=30)
        response.raise_for_status()

        Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Ошибка при загрузке {image_url}: {str(e)}")
        return False


def get_nasa_api_key():
    load_dotenv()
    return os.getenv('NASA_API_KEY')