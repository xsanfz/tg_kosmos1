import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import requests
from requests.exceptions import RequestException, HTTPError, Timeout

from space_utils import download_image, get_nasa_api_key, get_file_extension_from_url
from error_handlers import (
    handle_nasa_api_error,
    handle_data_format_error,
    handle_download_error,
    handle_config_error,
    handle_connection_error
)

# API and request constants
NASA_API_TIMEOUT_SECONDS = 15
NASA_API_MAX_IMAGES = 30
NASA_API_DEFAULT_IMAGES = 5
NASA_API_DATE_FORMAT = '%Y-%m-%d'
NASA_API_OUTPUT_DATE_FORMAT = '%Y%m%d'


def fetch_apod_images(api_key: str, image_count: int = NASA_API_DEFAULT_IMAGES) -> List[Dict]:
    response = requests.get(
        'https://api.nasa.gov/planetary/apod',
        params={
            'api_key': api_key,
            'count': image_count,
            'thumbs': True
        },
        timeout=NASA_API_TIMEOUT_SECONDS
    )
    response.raise_for_status()

    apod_entries = response.json()
    if not isinstance(apod_entries, list):
        raise ValueError("NASA API вернул неожиданный формат данных - ожидался список")

    return [item for item in apod_entries if item.get('media_type') == 'image']


def create_apod_filename(
        output_dir: Path,
        apod_date: str,
        image_url: str,
        fallback_index: int
) -> Path:
    try:
        publication_date = datetime.strptime(apod_date, NASA_API_DATE_FORMAT)
        date_prefix = publication_date.strftime(NASA_API_OUTPUT_DATE_FORMAT)
    except ValueError:
        date_prefix = f"no_date_{fallback_index}"

    if not image_url:
        raise ValueError("Невозможно создать имя файла - отсутствует URL изображения")

    file_extension = get_file_extension_from_url(image_url)
    return output_dir / f"apod_{date_prefix}{file_extension}"


def main():
    parser = argparse.ArgumentParser(
        description='Download Astronomy Picture of Day (APOD) from NASA',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--count',
        type=int,
        default=NASA_API_DEFAULT_IMAGES,
        help=f'Number of images to download (max {NASA_API_MAX_IMAGES})'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='nasa_apod',
        help='Directory to save downloaded images'
    )
    args = parser.parse_args()

    try:
        api_key = get_nasa_api_key()
        if not api_key:
            return

        try:
            apod_images = fetch_apod_images(api_key, min(args.count, NASA_API_MAX_IMAGES))
        except HTTPError as error:
            handle_nasa_api_error(f"{error.response.status_code}")
            return
        except Timeout:
            handle_connection_error("Превышено время ожидания ответа от NASA API")
            return
        except RequestException as error:
            handle_connection_error(str(error))
            return
        except ValueError as error:
            handle_data_format_error(str(error))
            return

        try:
            output_dir = Path(args.output)
            shutil.rmtree(output_dir, ignore_errors=True)
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            handle_nasa_api_error(f"Не удалось подготовить выходную директорию {args.output}: {error}")
            return

        print(f"Найдено {len(apod_images)} изображений. Начинаем загрузку...")

        success_count = 0
        for index, apod_entry in enumerate(apod_images, 1):
            image_url = apod_entry.get('hdurl') or apod_entry.get('url')
            if not image_url:
                print(f"Пропускаем элемент {index}: URL изображения не найден")
                continue

            try:
                output_path = create_apod_filename(
                    output_dir=output_dir,
                    apod_date=apod_entry.get('date', ''),
                    image_url=image_url,
                    fallback_index=index
                )
            except ValueError as error:
                print(f"Ошибка при создании имени файла для элемента {index}: {error}")
                continue

            try:
                download_result = download_image(image_url, str(output_path))
            except (RequestException, OSError, RuntimeError) as error:
                print(f"Ошибка при загрузке элемента {index}: {str(error)}")
                continue

            if download_result:
                success_count += 1
                print(f"Загружено: {output_path.name}")

        print(f"\nЗавершено. Успешно загружено {success_count} из {len(apod_images)} изображений")

    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")
        return


if __name__ == "__main__":
    main()