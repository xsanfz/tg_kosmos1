from pathlib import Path
from typing import List

# Supported image file extensions
IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'
}


def get_image_files(directory: Path) -> List[Path]:
    """
    Get all image files from the specified directory.
    
    Args:
        directory: Path to the directory containing images
        
    Returns:
        List of Path objects for all image files in the directory
    """
    if not directory.exists() or not directory.is_dir():
        return []
        
    return [
        file_path for file_path in directory.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS
    ] 