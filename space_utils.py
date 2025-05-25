import os
import shutil
from pathlib import Path
from urllib.parse import urlsplit, unquote
from typing import Dict, Optional

import requests
from dotenv import load_dotenv
from requests.exceptions import Timeout, HTTPError, RequestException


def get_file_extension_from_url(url: str) -> str:
    parsed = urlsplit(url)
    path = unquote(parsed.path)
    filename = os.path.split(path)[1]
    _, ext = os.path.splitext(filename)
    return ext.lower() if ext else '.jpg'


def download_image(
        image_url: str,
        save_path: str,
        params: Optional[Dict] = None,
        timeout: int = 30,
        stream: bool = True,
        raise_for_status: bool = True
) -> bool:
    try:
        response = requests.get(
            image_url,
            params=params,
            stream=stream,
            timeout=timeout
        )

        if raise_for_status:
            response.raise_for_status()

        Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)

        with open(save_path, 'wb') as f:
            if stream:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            else:
                f.write(response.content)

        return True

    except RequestException as e:
        if raise_for_status:
            raise
        return False


def get_nasa_api_key() -> Optional[str]:
    load_dotenv()
    return os.getenv('NASA_API_KEY')


def main():
    image_url = "https://apod.nasa.gov/apod/image/2205/JupiterDarkSpot_JunoGill_4000.jpg"
    save_path = "images/jupiter.jpg"

    try:
        download_image(image_url, save_path)
        print(f"Successfully downloaded image to {save_path}")

    except Timeout:
        print(f"Timeout occurred while downloading {image_url}")
    except HTTPError as e:
        print(f"HTTP Error {e.response.status_code} for {image_url}")
    except RequestException as e:
        print(f"Network error: {e}")
    except OSError as e:
        print(f"File system error: {e}")


if __name__ == "__main__":
    main()