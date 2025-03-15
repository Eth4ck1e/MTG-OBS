# src/gui/favorites_frame.py
import tkinter as tk
from tkinter import messagebox
from src.gui.base_frame import BaseCardFrame
from src.utils.favorites import load_favorites, save_favorite
from src.config.settings import THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, DECKS_DIR
import logging
import os


class FavoritesFrame(BaseCardFrame):
    def __init__(self, parent, browser, button_width=THUMBNAIL_WIDTH, button_height=THUMBNAIL_HEIGHT, padding=10):
        super().__init__(parent, browser, button_width, button_height, padding)
        self.config(borderwidth=2, relief="groove")
        self.widget_frame = tk.Frame(self, bg="lightgray")  # Container with visible background
        self.widget_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.create_widgets()
        self.load_favorites()
        logging.debug("FavoritesFrame initialized and packed")

    def create_widgets(self):
        """Create widgets for the Favorites frame."""
        logging.debug("Creating widgets in FavoritesFrame")
        self.label = tk.Label(self.widget_frame, text="Favorites", font=("Helvetica", 12, "bold"))
        self.label.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

        self.clear_button = tk.Button(self.widget_frame, text="Clear Favorites", command=self.clear_favorites, width=10)
        self.clear_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
        logging.debug("FavoritesFrame widgets created: label and clear_button")

    def load_favorites(self):
        """Load favorites from file on startup."""
        self.images = load_favorites(self.button_width, self.button_height)
        self.create_grid_of_buttons(show_fav_button=False)

    def add_card(self, card):
        """Add a card to the favorites frame."""
        if card.name not in [img.name for img in self.images]:
            self.images.append(card)
            self.create_grid_of_buttons(show_fav_button=False)

    def clear_favorites(self):
        """Clear all favorites from memory and file."""
        if not messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all favorites?"):
            logging.info("Clear favorites operation canceled by user")
            return
        try:
            self.images = []
            self.list_of_buttons = []
            self.create_grid_of_buttons()  # Refresh UI
            fav_file = os.path.join(DECKS_DIR, "favorites.txt")
            if os.path.exists(fav_file):
                with open(fav_file, "w") as f:
                    f.write("")  # Truncate file
                logging.debug("Cleared favorites.txt")
            logging.info("Favorites cleared successfully")
        except Exception as e:
            logging.error(f"Failed to clear favorites: {str(e)}", exc_info=True)