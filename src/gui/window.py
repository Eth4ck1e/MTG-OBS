# src/gui/window.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from src.gui.frame import Frame, FavoritesFrame
from src.gui.scryfall_search import ScryfallSearchFrame
from src.config.settings import DECKS_DIR, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
import logging

class Window(tk.Tk):
    def __init__(self, browser, title="Custom Window", width=DEFAULT_WINDOW_WIDTH, height=DEFAULT_WINDOW_HEIGHT, resizable=(True, True), *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.browser = browser
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(resizable[0], resizable[1])
        self.notebook = ttk.Notebook(self)
        self.decks_tab = ttk.Frame(self.notebook)
        self.log_tab = ttk.Frame(self.notebook)
        self.search_tab = ttk.Frame(self.notebook)
        self.favorites_frame = FavoritesFrame(self.decks_tab, self.browser)
        self.frame = Frame(self.decks_tab, self.browser, self.favorites_frame, self)
        self.search_frame = ScryfallSearchFrame(self.search_tab, self.browser, self.frame)
        self.log_text = tk.Text(self.log_tab, height=20, width=80)
        self.log_level = tk.StringVar(value="INFO")
        self.verbose = tk.BooleanVar(value=False)
        self.create_widgets()

    def create_widgets(self):
        self.notebook.add(self.decks_tab, text="Decks")
        self.notebook.add(self.log_tab, text="Log")
        self.notebook.add(self.search_tab, text="Scryfall Search", state="hidden")
        self.notebook.pack(fill="both", expand=True)

        self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.favorites_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        tk.Label(self.favorites_frame, text="Favorites", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        window_buttons = tk.Frame(self.decks_tab)
        window_buttons.pack(side=tk.BOTTOM, fill=tk.X)

        settings_frame = tk.Frame(window_buttons)
        settings_frame.pack(side=tk.RIGHT, pady=10, padx=10)
        tk.Label(settings_frame, text="Log Level:").pack(side=tk.LEFT)
        log_dropdown = ttk.Combobox(settings_frame, textvariable=self.log_level,
                                    values=["INFO", "WARNING", "ERROR"], state="readonly", width=10)
        log_dropdown.pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(settings_frame, text="Verbose", variable=self.verbose,
                       command=self.update_log_display).pack(side=tk.LEFT)

        self.log_text.pack(fill="both", expand=True)
        self.search_frame.pack(fill="both", expand=True)
        self.update_log_display()

    def update_log_display(self):
        self.log_text.delete(1.0, tk.END)
        level = self.log_level.get()
        log_file = os.path.join(DECKS_DIR, "..", "logs", "app.log")
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                for line in f:
                    if (level == "INFO" or
                        (level == "WARNING" and "WARNING" in line) or
                        (level == "ERROR" and "ERROR" in line)):
                        if self.verbose.get() or "ERROR" in line or "WARNING" in line:
                            self.log_text.insert(tk.END, line)

    def show_scryfall_search(self, card_name, set_code, index):
        self.notebook.tab(self.search_tab, state="normal")
        self.notebook.select(self.search_tab)
        self.search_frame.search_scryfall(card_name, set_code, index)