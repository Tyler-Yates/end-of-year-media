import os.path
import shutil
from pathlib import Path
from typing import Optional

import pyexiv2


class ImageUtil:
    def __init__(self, folder_root: str):
        self.folder_root = folder_root

        self.year = os.path.basename(self.folder_root)
        if self.year.isdigit() and len(self.year) == 4:
            self.highlights_orig_folder = os.path.join(self.folder_root, f"{self.year} Highlights", "Originals")
        else:
            raise ValueError(f"Folder is not a date: {self.year}")

    def find_images(self) -> list[Path]:
        """
        Finds images in the folder root and returns them sorted by date taken.

        Returns:
            The list of images
        """

        supported_formats = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".rw2")
        files = list(Path(self.folder_root).rglob("*"))  # Get all files in folder
        images = [file for file in files if file.suffix.lower() in supported_formats]
        print(f"Found {len(images)} files with supported types")

        # If there are multiple versions of the same file name, prefer rw2 files
        grouped_files = {}
        for file in images:
            base_name = file.stem.lower()
            if base_name not in grouped_files or file.suffix.lower() == ".rw2":
                grouped_files[base_name] = file

        print(f"Found {len(grouped_files)} files after de-duping")

        # Extract dates and sort
        print("Sorting by date taken...")
        # TODO bring this back
        sorted_images = list(grouped_files.values())
        # sorted_images = sorted(
        #     grouped_files.values(),
        #     key=lambda x: self.get_date_taken(str(x)) or "9999:99:99 99:99:99"  # Use a large value for missing EXIF
        # )
        print("Finished sorting")
        return sorted_images

    def save_image(self, image_path: Path):
        print(f"Saving file {image_path}")
        os.makedirs(self.highlights_orig_folder, exist_ok=True)
        shutil.copy(image_path, os.path.join(self.highlights_orig_folder))

    @staticmethod
    def get_date_taken(file_path: str) -> Optional[str]:
        """
        Get the date the photo was taken using EXIF data.

        Args:
            file_path: the path to the file

        Returns:
            The string of the date taken or None if not present
        """

        try:
            metadata = pyexiv2.Image(file_path)
            exif = metadata.read_exif()
            return exif.get("Exif.Photo.DateTimeOriginal")
        except Exception as e:
            print(f"Error reading EXIF data from {file_path}: {e}")
        return None
