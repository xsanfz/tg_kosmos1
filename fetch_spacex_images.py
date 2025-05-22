import argparse
import shutil
from pathlib import Path
from typing import List
from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException


def fetch_spacex_launch_image_urls(launch_id: str = 'latest') -> List[str]:
    api_base_url = 'https://api.spacexdata.com/v4/launches/'
    launch_api_url = f'{api_base_url}{launch_id}'

    response = requests.get(launch_api_url, timeout=10)
    response.raise_for_status()
    launch_details = response.json()

    if not isinstance(launch_details, dict):
        raise ValueError("Invalid API response format")

    flickr_photos = launch_details.get('links', {}).get('flickr', {})
    image_urls = flickr_photos.get('original', [])

    if not isinstance(image_urls, list):
        raise ValueError("Invalid image data format")

    return image_urls


def extract_file_extension_from_url(url: str) -> str:
    return Path(urlparse(url).path).suffix


def download_image(image_url: str, save_path: str) -> None:
    response = requests.get(image_url, stream=True)
    response.raise_for_status()

    with open(save_path, 'wb') as output_file:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, output_file)


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

    try:
        try:
            flickr_image_urls = fetch_spacex_launch_image_urls(args.launch_id)
        except ValueError as error:
            print(f"Data processing error: {str(error)}")
            return
        except RequestException as error:
            print(f"SpaceX API request failed: {str(error)}")
            return

        if not flickr_image_urls:
            print("No Flickr images available for this launch")
            return

        output_dir = Path(args.output_dir)
        shutil.rmtree(output_dir, ignore_errors=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Found {len(flickr_image_urls)} images. Starting download...")

        success_count = 0
        for idx, image_url in enumerate(flickr_image_urls, start=1):
            try:
                file_extension = extract_file_extension_from_url(image_url)
                image_filename = output_dir / f"spacex_{idx}{file_extension}"
                download_image(image_url, str(image_filename))
                success_count += 1
                print(f"Downloaded: {image_filename.name}")
            except Exception as error:
                print(f"Failed to download image {idx}: {str(error)}")

        print(f"\nDownload complete. Success: {success_count}/{len(flickr_image_urls)}")

    except OSError as error:
        print(f"File system operation failed: {str(error)}")
    except Exception as error:
        print(f"Unexpected error occurred: {str(error)}")


if __name__ == "__main__":
    main()