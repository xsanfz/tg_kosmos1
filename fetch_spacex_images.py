import argparse
import shutil
from pathlib import Path
from typing import List

import requests
from requests.exceptions import RequestException, HTTPError
from space_utils import get_file_extension_from_url


def fetch_spacex_launch_image_urls(launch_id: str = 'latest') -> List[str]:
    api_base_url = 'https://api.spacexdata.com/v4/launches/'
    launch_api_url = f'{api_base_url}{launch_id}'

    response = requests.get(launch_api_url, timeout=10)
    response.raise_for_status()

    launch_details = response.json()

    flickr_photos = launch_details.get('links', {}).get('flickr', {})
    image_urls = flickr_photos.get('original', [])

    if not isinstance(image_urls, list):
        raise TypeError("Image data is not a list")

    return image_urls


def download_image(image_url: str, save_path: str) -> None:
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()
    except RequestException as e:
        raise RuntimeError(f"Failed to download image: {e}")

    try:
        with open(save_path, 'wb') as output_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, output_file)
    except OSError as e:
        raise RuntimeError(f"Failed to save image: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Download SpaceX launch photos',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--launch-id',
        help='Specific launch ID (default: latest launch)',
        default='latest'
    )
    parser.add_argument(
        '--output-dir',
        help='Directory to save downloaded images',
        default='spacex_images'
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    try:
        shutil.rmtree(output_dir, ignore_errors=True)
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Failed to create output directory: {e}")
        return

    try:
        flickr_image_urls = fetch_spacex_launch_image_urls(args.launch_id)
    except (RequestException, ValueError, TypeError) as e:
        print(f"Error fetching SpaceX launch data: {e}")
        return

    if not flickr_image_urls:
        print("No images found for this launch.")
        return

    print(f"Found {len(flickr_image_urls)} images. Downloading...")

    success_count = 0
    for idx, image_url in enumerate(flickr_image_urls, start=1):
        try:
            file_extension = get_file_extension_from_url(image_url)
            image_filename = output_dir / f"spacex_{idx}{file_extension}"
            download_image(image_url, str(image_filename))
            success_count += 1
            print(f"Downloaded: {image_filename.name}")
        except (RequestException, OSError, RuntimeError) as e:
            print(f"Failed to download image {idx}: {e}")

    print(f"\nResults: {success_count} successful, {len(flickr_image_urls) - success_count} failed")


if __name__ == "__main__":
    main()