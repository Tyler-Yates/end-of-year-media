import io
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import rawpy
from PIL import Image, ImageTk

from app.image_util import ImageUtil

WINDOW_WIDTH_PX = 1920
WINDOW_HEIGHT_PX = 1200


class Gui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Preview - Sorted by Date Taken")
        self.root.geometry(f"{WINDOW_WIDTH_PX}x{WINDOW_HEIGHT_PX}")

        # Create a label to display the image
        self.images = []
        self.current_index = 0
        self.image_label = tk.Label(self.root)
        self.image_label.pack(expand=True, fill=tk.BOTH)

        # Create a button to browse a folder
        browse_button = tk.Button(self.root, text="Browse Folder", command=lambda: self._browse_folder())
        browse_button.pack(pady=10)

        # Bind arrow keys for navigation
        self.root.bind("<Left>", self._on_left_arrow)
        self.root.bind("<Right>", self._on_right_arrow)

    def run(self):
        self.root.mainloop()

    def _display_image(self, image_path: Path):
        """Display the selected image in the GUI."""
        try:
            if image_path.suffix.lower() == ".rw2":
                img = self._open_raw_image(image_path)
            else:
                img = Image.open(image_path)

            img.thumbnail((WINDOW_WIDTH_PX - 100, WINDOW_HEIGHT_PX - 100))  # Resize to fit the window
            img_tk = ImageTk.PhotoImage(img)

            # Update the image label
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk
        except Exception as e:
            print(f"Failed to display image: {e}")

    @staticmethod
    def _open_raw_image(rw2_path: Path) -> Image:
        """Open a RW2 raw image and convert it to a Pillow image."""
        with rawpy.imread(str(rw2_path)) as raw:
            # Extract the thumbnail image directly from the RAW file which is very fast
            thumb = raw.extract_thumb()

            # Convert the thumbnail to a BytesIO object to pass it to Pillow
            thumb_data = thumb.data
            thumb_io = io.BytesIO(thumb_data)
            img = Image.open(thumb_io)
            img = img.convert("RGB")
        return img

    def _browse_folder(self):
        """Open a folder dialog, find images, and display the first one."""
        folder_path = filedialog.askdirectory(title="Select Folder")
        if not folder_path:
            return

        print(f"Finding images in dir {folder_path}...")
        image_util = ImageUtil(folder_path)

        self.images = image_util.find_images()
        if self.images:
            self._display_image(self.images[0])
        else:
            messagebox.showinfo("No Images Found", "No valid image files were found in the selected folder.")

    def _on_left_arrow(self, event):
        """Move to the previous image when the left arrow key is pressed."""
        if self.images:
            self.current_index = (self.current_index - 1) % len(self.images)
            self._display_image(self.images[self.current_index])

    def _on_right_arrow(self, event):
        """Move to the next image when the right arrow key is pressed."""
        if self.images:
            self.current_index = (self.current_index + 1) % len(self.images)
            self._display_image(self.images[self.current_index])
