from pathlib import Path
from typing import List, Optional, Union
import random
import sys

def get_image_files(
        directory: Path,
        photo_name: Optional[str] = None,
        extensions: Optional[List[str]] = None
) -> Union[Optional[Path], List[Path]]:
    if not directory.exists():
        raise FileNotFoundError(f"Директория {directory} не существует.")
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} не является директорией.")

    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

    if photo_name:
        image_path = directory / photo_name
        if not image_path.exists():
            raise FileNotFoundError(f"Изображение {image_path} не найдено.")
        return image_path

    images = [
        file for file in directory.iterdir()
        if file.is_file() and file.suffix.lower() in extensions
    ]

    return images

def get_random_image(directory: Path) -> Optional[Path]:
    images = get_image_files(directory)
    if not images:
        raise ValueError(f"В директории {directory} нет подходящих изображений.")
    return random.choice(images)

def main():
    try:
        image_dir = Path("images")

        all_images = get_image_files(image_dir)
        print("Все изображения в директории:")
        for img in all_images:
            print(f" - {img.name}")

        specific_image = get_image_files(image_dir, "example.jpg")
        print(f"\nНайдено конкретное изображение: {specific_image}")

        random_image = get_random_image(image_dir)
        print(f"\nСлучайное изображение: {random_image.name}")

    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()