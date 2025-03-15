# src/gui/deck_controls_frame.py
import tkinter as tk
from tkinter import ttk, filedialog
import logging

class DeckControlsFrame(tk.Frame):
    """Frame for deck control buttons and search bar."""

    def __init__(self, parent, deck_frame, favorites_frame, padding=10):
        super().__init__(parent, bg="lightgray")
        self.deck_frame = deck_frame
        self.favorites_frame = favorites_frame
        self.padding = padding
        self.create_widgets()
        logging.debug("DeckControlsFrame initialized")

    def create_widgets(self):
        """Create control widgets."""
        logging.debug("Creating widgets in DeckControlsFrame")
        reload_button = tk.Button(self, text="Reload", command=self.deck_frame.reload_images, width=10)
        reload_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

        clear_button = tk.Button(self, text="Clear All", command=self.deck_frame.clear_all, width=10)
        clear_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

        clear_fav_button = tk.Button(self, text="Clear Favorites", command=self.favorites_frame.clear_favorites, width=10)
        clear_fav_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

        add_deck_button = tk.Button(self, text="Add Deck", command=self.deck_frame.add_deck, width=10)
        add_deck_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

        search_label = tk.Label(self, text="Search:", bg="lightgray")
        search_label.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

        self.search_field = tk.Entry(self, width=50)
        self.search_field.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
        self.search_field.bind("<KeyRelease>", lambda event: self.deck_frame.filter_cards(event))  # Pass event to filter_cards