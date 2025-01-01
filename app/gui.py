import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import rawpy
from PIL import Image, ImageTk

from app.image_util import ImageUtil


class Gui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Preview - Sorted by Date Taken")
        self.root.geometry("800x600")

        # Create a label to display the image
        self.image_label = tk.Label(self.root)
        self.image_label.pack(expand=True, fill=tk.BOTH)

        # Create a button to browse a folder
        browse_button = tk.Button(self.root, text="Browse Folder", command=lambda: self._browse_folder())
        browse_button.pack(pady=10)

    def run(self):
        self.root.mainloop()

    def _display_image(self, image_path: Path):
        """Display the selected image in the GUI."""
        try:
            if image_path.suffix.lower() == ".rw2":
                img = self._open_raw_image(image_path)
            else:
                img = Image.open(image_path)

            img.thumbnail((800, 600))  # Resize to fit the window
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
            rgb = raw.postprocess()
            # Convert the numpy array (RGB) to a Pillow image
            img = Image.fromarray(rgb)
        return img

    def _browse_folder(self):
        """Open a folder dialog, find images, and display the first one."""
        folder_path = filedialog.askdirectory(title="Select Folder")
        if not folder_path:
            return

        print(f"Finding images in dir {folder_path}...")
        image_util = ImageUtil(folder_path)

        images = image_util.find_images()
        if images:
            self._display_image(images[0])
            # Add navigation buttons
            self._setup_navigation_buttons(images)
        else:
            messagebox.showinfo("No Images Found", "No valid image files were found in the selected folder.")

    def _setup_navigation_buttons(self, images):
        """Set up navigation buttons to browse through images."""

        def show_next():
            nonlocal current_index
            current_index = (current_index + 1) % len(images)
            self._display_image(images[current_index])

        def show_prev():
            nonlocal current_index
            current_index = (current_index - 1) % len(images)
            self._display_image(images[current_index])

        # Starting index
        current_index = 0

        # Create buttons for navigation
        next_button = tk.Button(self.root, text="Next", command=show_next)
        next_button.pack(side=tk.RIGHT, padx=10, pady=10)

        prev_button = tk.Button(self.root, text="Previous", command=show_prev)
        prev_button.pack(side=tk.LEFT, padx=10, pady=10)
