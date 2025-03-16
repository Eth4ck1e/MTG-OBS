# src/gui/favorites_frame.py
import tkinter as tk
from tkinter import messagebox
from src.gui.base_frame import BaseCardFrame
from src.utils.favorites import load_favorites, save_favorite
from src.config.settings import CARD_WIDTH, CARD_HEIGHT, DECKS_DIR, PRIMARY_BG_COLOR, TEXT_COLOR, BOLD_FONT
import logging
import os

class FavoritesFrame(BaseCardFrame):
    def __init__(self, parent, browser, button_width=CARD_WIDTH, button_height=CARD_HEIGHT, padding=10):
        super().__init__(parent, browser, button_width, button_height, padding)
        self.config(bg=PRIMARY_BG_COLOR, borderwidth=2, relief="groove")
        self.create_widgets()
        self.load_favorites()

    def create_widgets(self):
        """Create widgets for the Favorites frame with modern styling."""
        logging.debug("Creating widgets in FavoritesFrame")
        self.label = tk.Label(self, text="Favorites", font=BOLD_FONT, bg=PRIMARY_BG_COLOR, fg=TEXT_COLOR)
        self.label.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

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
            self.create_grid_of_buttons()
            fav_file = os.path.join(DECKS_DIR, "favorites.txt")
            if os.path.exists(fav_file):
                with open(fav_file, "w") as f:
                    f.write("")
                logging.debug("Cleared favorites.txt")
            logging.info("Favorites cleared successfully")
        except Exception as e:
            logging.error(f"Failed to clear favorites: {str(e)}", exc_info=True)