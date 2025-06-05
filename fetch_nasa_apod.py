import argparse
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime

import requests
from requests.exceptions import RequestException, HTTPError, Timeout

from space_utils import download_image, get_nasa_api_key, get_file_extension_from_url


def fetch_apod_images(api_key: str, image_count: int = 30) -> List[Dict]:
    response = requests.get(
        'https://api.nasa.gov/planetary/apod',
        params={
            'api_key': api_key,
            'count': image_count,
            'thumbs': True
        },
        timeout=15
    )
    response.raise_for_status()

    apod_items = response.json()
    if not isinstance(apod_items, list):
        raise ValueError("Invalid API response format")

    return [item for item in apod_items if item.get('media_type') == 'image']


def create_apod_filename(
        output_dir: Path,
        apod_date: str,
        image_url: str,
        fallback_index: int
) -> Path:
    try:
        publication_date = datetime.strptime(apod_date, '%Y-%m-%d')
        date_prefix = publication_date.strftime('%Y%m%d')
    except ValueError:
        date_prefix = f"no_date_{fallback_index}"

    if not image_url:
        raise ValueError("Image URL must be provided")

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
        default=5,
        help='Number of images to download (max 30)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='nasa_apod',
        help='Directory to save downloaded images'
    )
    args = parser.parse_args()

    api_key = get_nasa_api_key()
    if not api_key:
        print("Configuration error: NASA API key not found. Check .env file")
        return

    try:
        apod_images = fetch_apod_images(api_key, min(args.count, 30))
    except HTTPError as error:
        print(f"NASA API error: {error.response.status_code}")
        if error.response.status_code == 403:
            print("Please verify your API key")
        return
    except Timeout:
        print("Request to NASA API timed out")
        return
    except RequestException as error:
        print(f"Connection error: {str(error)}")
        return
    except ValueError as error:
        print(f"Data error: {str(error)}")
        return

    if not apod_images:
        print("No suitable images found")
        return

    try:
        output_dir = Path(args.output)
        shutil.rmtree(output_dir, ignore_errors=True)
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"Filesystem error: {str(error)}")
        return

    print(f"Found {len(apod_images)} images. Starting download...")

    success_count = 0
    for index, image_metadata in enumerate(apod_images, 1):
        try:
            image_url = image_metadata.get('hdurl') or image_metadata.get('url')
            if not image_url:
                print(f"Skipping item {index}: Image URL not found")
                continue

            output_path = create_apod_filename(
                save_directory=output_dir,
                date_string=image_metadata.get('date', ''),
                image_url=image_url,
                item_index=index
            )

            if download_image(image_url, str(output_path)):
                success_count += 1
                print(f"Downloaded: {output_path.name}")
        except (RequestException, OSError, ValueError) as error:
            print(f"Error downloading item {index}: {str(error)}")

    print(f"\nCompleted. Successfully downloaded {success_count} of {len(apod_images)} images")


if __name__ == "__main__":
    main()