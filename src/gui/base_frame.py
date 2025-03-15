# src/gui/base_frame.py
import tkinter as tk
from tkinter import ttk
from src.utils.paths import get_relative_path
from src.utils.image import CustomImage, create_clear_png
from src.config.settings import THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, CACHE_DIR
from PIL import Image  # Add explicit import
import logging


class BaseCardFrame(tk.Frame):
    """Base class for card frames with shared functionality."""

    def __init__(self, parent, browser, button_width=THUMBNAIL_WIDTH, button_height=THUMBNAIL_HEIGHT, padding=10):
        tk.Frame.__init__(self, parent)
        self.browser = browser
        self.button_width = button_width
        self.button_height = button_height
        self.padding = padding
        self.images = []
        self.list_of_buttons = []  # Stores (label, name_label) tuples

    def create_grid_of_buttons(self, target_frame=None, show_fav_button=False):
        """Create grid of card buttons in the specified frame (defaults to self)."""
        frame = target_frame if target_frame is not None else self
        for widget in frame.winfo_children():
            widget.destroy()
        self.list_of_buttons = []
        for index, image in enumerate(self.images):
            filename = image.name
            label = tk.Label(frame, image=image.thumbnail,
                             width=self.button_width, height=self.button_height)
            display_name = " ".join(filename.replace("_", " ").split(" ")[0:-2])
            label_name = tk.Label(label, text=display_name, fg="white", font=("Helvetica", 10), bg="#333333")
            label_name.place(relx=0.5, rely=0.5, anchor="center")
            if show_fav_button and hasattr(self, 'add_to_favorites'):
                fav_button = tk.Button(label, text="Fav", command=lambda x=index: self.add_to_favorites(x), width=3)
                fav_button.place(relx=0.5, rely=0.0, anchor='n')
            slot1_button = tk.Button(label, text="SLOT 1",
                                     command=lambda x=index: self.set_slot(0, self.images[x].name))
            slot1_button.place(relx=0.0, rely=1.0, anchor='sw')
            slot2_button = tk.Button(label, text="SLOT 2",
                                     command=lambda x=index: self.set_slot(1, self.images[x].name))
            slot2_button.place(relx=1.0, rely=1.0, anchor='se')
            if hasattr(self, 'replace_card'):
                menu = tk.Menu(label, tearoff=0)
                menu.add_command(label="Replace Card", command=lambda i=index: self.replace_card(i))
                label.bind("<Button-3>", lambda e, m=menu: m.tk_popup(e.x_root, e.y_root))
            self.list_of_buttons.append((label, label_name))
            label.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
        logging.debug(f"Created {len(self.list_of_buttons)} buttons")

    def set_slot(self, slot, filename):
        path = get_relative_path(CACHE_DIR, filename)
        try:
            with Image.open(path) as img:
                width, height = img.size
                logging.debug(f"Setting slot {slot} to {path} (size: {width}x{height}px)")
        except Exception as e:
            logging.warning(f"Could not check image size for {path}: {str(e)}")

        clear_url = create_clear_png()
        if slot == 0:  # Slot 1: Push current slot 1 to slot 2
            current_slot1 = self.browser.get_slot(0)
            if current_slot1 and current_slot1 != clear_url:
                logging.debug(f"Pushing slot 1 ({current_slot1}) to slot 2")
                self.browser.set_slot(1, current_slot1)
            self.browser.set_slot(0, path)
        elif slot == 1:  # Slot 2: Replace directly
            self.browser.set_slot(1, path)
        else:
            logging.warning(f"Invalid slot index: {slot}")
            return