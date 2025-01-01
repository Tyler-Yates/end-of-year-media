import json
import os.path
import shutil
from datetime import datetime
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

        self.exif_cache_filename = f"{self.year}_exif_cache.json"
        self.exif_cache = self._load_exif_cache_if_present()
        self.new_exif_files = 0

    def _save_exif_cache(self):
        try:
            with open(self.exif_cache_filename, "w") as f:
                json.dump(self.exif_cache, f, indent=4)
            print(f"exif cache saved to {self.exif_cache_filename} with {len(self.exif_cache)} entries")
        except Exception as e:
            print(f"Failed to save exif cache: {e}")

    def _load_exif_cache_if_present(self) -> dict[str, str]:
        if not os.path.exists(self.exif_cache_filename):
            return dict()

        try:
            with open(self.exif_cache_filename, "r") as f:
                loaded_dict = json.load(f)
            print(f"Exif cache loaded from {self.exif_cache_filename} with {len(loaded_dict)} entries")
            return loaded_dict
        except Exception as e:
            print(f"Failed to load Exif cache: {e}")
            return dict()

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

        sorted_images = sorted(
            grouped_files.values(),
            key=lambda x: self.get_date_taken(str(x)) or "9999:99:99 99:99:99",  # Use a large value for missing EXIF
        )

        # Save the exif cache since reading exif data is very expensive
        self._save_exif_cache()

        print("Finished sorting")
        return sorted_images

    def save_image(self, image_path: Path):
        print(f"Saving file {image_path}")
        os.makedirs(self.highlights_orig_folder, exist_ok=True)
        shutil.copy(image_path, os.path.join(self.highlights_orig_folder))

    @staticmethod
    def _get_file_modified_time(file_path: str) -> Optional[str]:
        """
        Get the file's modified time as a string in the format 'YYYY:MM:DD HH:MM:SS'.
        """
        try:
            # Get file modified time and format it to match EXIF datetime format
            modified_timestamp = os.path.getmtime(file_path)
            modified_time = datetime.fromtimestamp(modified_timestamp).strftime("%Y:%m:%d %H:%M:%S")
            return modified_time
        except Exception as e:
            print(f"Error getting modified time for {file_path}: {e}")
            return None

    def get_date_taken(self, file_path: str) -> Optional[str]:
        """
        Get the date the photo was taken using EXIF data.

        Args:
            file_path: the path to the file

        Returns:
            The string of the date taken or None if not present
        """
        if file_path in self.exif_cache:
            return self.exif_cache[file_path]

        date_taken = None
        try:
            metadata = pyexiv2.Image(file_path)
            exif = metadata.read_exif()
            date_taken = exif.get("Exif.Photo.DateTimeOriginal")
        except Exception as e:
            print(f"Error reading EXIF data from {file_path}: {e}")

        # Fall back on modified date if Exif fails
        if not date_taken:
            date_taken = self._get_file_modified_time(file_path)

        if date_taken:
            self.exif_cache[file_path] = date_taken
            self.new_exif_files += 1
            if self.new_exif_files >= 100:
                self._save_exif_cache()
                self.new_exif_files = 0

        return date_taken
