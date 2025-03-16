# src/gui/deck_controls_frame.py
import tkinter as tk
from tkinter import ttk
import logging
from src.config.settings import SECONDARY_BG_COLOR, WIDGET_BG_COLOR, WIDGET_ACTIVE_COLOR, TEXT_COLOR, DEFAULT_FONT, \
    FIELD_BG_COLOR, CONTROL_TEXT_COLOR


class DeckControlsFrame(tk.Frame):
    """Frame for deck control buttons and search bar."""

    def __init__(self, parent, deck_frame, favorites_frame, padding=10):
        super().__init__(parent, bg=SECONDARY_BG_COLOR)
        self.deck_frame = deck_frame
        self.favorites_frame = favorites_frame
        self.padding = padding
        self.create_widgets()
        logging.debug("DeckControlsFrame initialized")

    def create_widgets(self):
        """Create control widgets with modern styling."""
        logging.debug("Creating widgets in DeckControlsFrame")

        style = ttk.Style()
        style.configure("Modern.TButton", font=DEFAULT_FONT, padding=5, background=WIDGET_BG_COLOR,
                        foreground=CONTROL_TEXT_COLOR)
        style.map("Modern.TButton", background=[("active", WIDGET_ACTIVE_COLOR)])

        reload_button = ttk.Button(self, text="Reload", command=self.deck_frame.reload_images, style="Modern.TButton")
        reload_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

        clear_button = ttk.Button(self, text="Clear All", command=self.deck_frame.clear_all, style="Modern.TButton")
        clear_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

        clear_fav_button = ttk.Button(self, text="Clear Favorites", command=self.favorites_frame.clear_favorites,
                                      style="Modern.TButton")
        clear_fav_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

        add_deck_button = ttk.Button(self, text="Add Deck", command=self.deck_frame.add_deck, style="Modern.TButton")
        add_deck_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

        search_label = tk.Label(self, text="Search:", bg=SECONDARY_BG_COLOR, fg=TEXT_COLOR, font=DEFAULT_FONT)
        search_label.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

        self.search_field = tk.Entry(self, width=50, bg=FIELD_BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                     font=DEFAULT_FONT)
        self.search_field.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
        self.search_field.bind("<KeyRelease>", lambda event: self.deck_frame.filter_cards(event))