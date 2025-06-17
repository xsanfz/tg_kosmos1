from pathlib import Path
from typing import List, Optional, Union
import random
import sys
import requests
import os
import shutil
from urllib.parse import urlparse
from error_handlers import handle_directory_error, handle_download_error, handle_config_error
from env_utils import get_env_variable
from image_tools import get_image_files


def download_image(url: str, filepath: Path, timeout: int = 10) -> bool:
    response = requests.get(url, stream=True, timeout=timeout)
    response.raise_for_status()

    with open(filepath, 'wb') as output_file:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, output_file)
    return True


def get_file_extension_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path
    return os.path.splitext(path)[1]