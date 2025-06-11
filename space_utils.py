from pathlib import Path
from typing import List, Optional, Union
import random
import sys
import requests
import os
from urllib.parse import urlparse
from error_handlers import handle_directory_error, handle_download_error, handle_config_error
from env_utils import get_env_variable
from image_tools import get_image_files


def download_image(url: str, filepath: Path) -> bool:
    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            f.write(response.content)
        return True
    except requests.RequestException as e:
        handle_download_error(f"Не удалось загрузить изображение с {url}: {str(e)}")
        return False
    except IOError as e:
        handle_download_error(f"Не удалось сохранить изображение в {filepath}: {str(e)}")
        return False


def get_nasa_api_key() -> str:
    return get_env_variable('NASA_API_KEY')


def get_file_extension_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path
    return os.path.splitext(path)[1]