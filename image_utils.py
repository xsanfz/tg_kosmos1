from pathlib import Path
from typing import List, Optional, Union
import random


def get_image_files(
        directory: Path,
        photo_name: Optional[str] = None,
        extensions: Optional[List[str]] = None
) -> Union[Optional[Path], List[Path]]:
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

    if photo_name:
        image_path = directory / photo_name
        return image_path if image_path.exists() else None

    images = [
        file for file in directory.iterdir()
        if file.is_file() and file.suffix.lower() in extensions
    ]

    return images


def get_random_image(directory: Path) -> Optional[Path]:
    images = get_image_files(directory)
    return random.choice(images) if images else None


def main():
    image_dir = Path("images")

    all_images = get_image_files(image_dir)
    print("Все изображения в директории:")
    for img in all_images:
        print(f" - {img.name}")

    specific_image = get_image_files(image_dir, "example.jpg")
    if specific_image:
        print(f"\nНайдено конкретное изображение: {specific_image}")
    else:
        print("\nКонкретное изображение не найдено")

    random_image = get_random_image(image_dir)
    if random_image:
        print(f"\nСлучайное изображение: {random_image.name}")
    else:
        print("\nВ директории нет изображений")


if __name__ == "__main__":
    main()