import os
from pathlib import Path
from urllib.parse import urlsplit, unquote
import shutil

import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from dotenv import load_dotenv


def get_file_extension_from_url(url: str) -> str:
    parsed = urlsplit(url)
    path = unquote(parsed.path)
    filename = os.path.split(path)[1]
    _, ext = os.path.splitext(filename)
    return ext.lower() if ext else '.jpg'


def download_image(image_url: str, save_path: str) -> bool:
    try:
        response = requests.get(image_url, stream=True, timeout=30)
        response.raise_for_status()

        Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)

        with open(save_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        return True

    except Timeout:
        print(f"Timeout error while downloading {image_url}")
    except HTTPError as e:
        print(f"HTTP error (status {e.response.status_code}) for {image_url}: {e}")
    except RequestException as e:
        print(f"Network-related error while downloading {image_url}: {e}")
    except OSError as e:
        print(f"File system error while saving {save_path}: {e}")
    except Exception as e:
        print(f"Unexpected error while downloading {image_url}: {e}")

    return False


def get_nasa_api_key() -> str | None:
    load_dotenv()
    return os.getenv('NASA_API_KEY')