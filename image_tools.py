from pathlib import Path
from typing import List

IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'
}


def get_image_files(directory: Path) -> List[Path]:
    if not directory.exists() or not directory.is_dir():
        return []
        
    return [
        file_path for file_path in directory.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS
    ] 