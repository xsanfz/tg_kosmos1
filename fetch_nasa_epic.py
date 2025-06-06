import argparse
import shutil
from pathlib import Path
from datetime import datetime
import requests
from typing import List, Dict
from space_utils import download_image, get_nasa_api_key


def fetch_epic_images(api_key: str, max_images: int = 10) -> List[Dict]:
    api_endpoint = 'https://api.nasa.gov/EPIC/api/natural/images'
    response = requests.get(api_endpoint, params={'api_key': api_key}, timeout=15)
    response.raise_for_status()
    return response.json()[:max_images]


def generate_epic_image_url(
        image_date: str,
        image_name: str
) -> str:
    capture_date = datetime.strptime(image_date, "%Y-%m-%d %H:%M:%S")
    return (
        f"https://api.nasa.gov/EPIC/archive/natural/"
        f"{capture_date:%Y/%m/%d}/png/{image_name}.png"
    )


def main():
    parser = argparse.ArgumentParser(
        description='Download NASA EPIC Earth imagery',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='Number of images to download (max 10)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='nasa_epic',
        help='Directory to save downloaded images'
    )
    args = parser.parse_args()

    nasa_api_key = get_nasa_api_key()
    output_directory = Path(args.output)

    shutil.rmtree(output_directory, ignore_errors=True)
    output_directory.mkdir(parents=True, exist_ok=True)

    images = fetch_epic_images(nasa_api_key, min(args.count, 10))
    print(f"Found {len(images)} images. Downloading...")

    downloaded_count = 0
    for image_number, image in enumerate(images, 1):
        image_url = generate_epic_image_url(
            image_date=image['date'],
            image_name=image['image']
        )
        filename = output_directory / f"epic_{image_number}_{image['image']}.png"

        download_image(
            image_url=image_url,
            save_path=str(filename),
            params={'api_key': nasa_api_key},
            timeout=15
        )

        downloaded_count += 1
        print(f"Downloaded: {filename.name}")

    print(f"\nDone. Successfully downloaded {downloaded_count}/{len(images)} images")


if __name__ == "__main__":
    main()