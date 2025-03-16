# src/gui/window.py
import os
import tkinter as tk
from tkinter import ttk, filedialog
from src.gui.deck_frame import Frame
from src.gui.favorites_frame import FavoritesFrame
from src.gui.deck_controls_frame import DeckControlsFrame
from src.gui.scryfall_search import ScryfallSearchFrame
from src.config.settings import DECKS_DIR, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, WINDOW_TITLE, PRIMARY_BG_COLOR, SECONDARY_BG_COLOR, TEXT_COLOR, FIELD_BG_COLOR, WIDGET_ACTIVE_COLOR, DEFAULT_FONT, CONTROL_TEXT_COLOR
import logging
import yaml

class Window(tk.Tk):
    def __init__(self, browser, title=WINDOW_TITLE, width=DEFAULT_WINDOW_WIDTH, height=DEFAULT_WINDOW_HEIGHT, resizable=(True, True), *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.browser = browser
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(resizable[0], resizable[1])
        self.configure(bg=PRIMARY_BG_COLOR)
        self.notebook = ttk.Notebook(self)
        style = ttk.Style()
        style.configure("TNotebook", background=PRIMARY_BG_COLOR, foreground=CONTROL_TEXT_COLOR)
        style.configure("TNotebook.Tab", background=SECONDARY_BG_COLOR, foreground=CONTROL_TEXT_COLOR, padding=[5, 2])
        style.map("TNotebook.Tab", background=[("selected", WIDGET_ACTIVE_COLOR)])
        self.decks_tab = ttk.Frame(self.notebook)
        self.log_tab = ttk.Frame(self.notebook)
        self.search_tab = ttk.Frame(self.notebook)
        self.favorites_frame = FavoritesFrame(self.decks_tab, self.browser)
        self.frame = Frame(self.decks_tab, self.browser, self.favorites_frame, self)
        self.controls_frame = DeckControlsFrame(self.decks_tab, self.frame, self.favorites_frame)
        self.search_frame = ScryfallSearchFrame(self.search_tab, self.browser, self.frame, self.notebook)
        self.log_text = tk.Text(self.log_tab, height=20, width=80, bg=FIELD_BG_COLOR, fg=TEXT_COLOR, font=DEFAULT_FONT)
        self.log_level = tk.StringVar(value="INFO")
        self.verbose = tk.BooleanVar(value=False)
        self.config_file = os.path.join(DECKS_DIR, "..", "config.yml")
        self.load_config()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.notebook.add(self.decks_tab, text="Decks")
        self.notebook.add(self.log_tab, text="Log")
        self.notebook.add(self.search_tab, text="Scryfall Search")
        self.notebook.pack(side=tk.TOP, fill="both", expand=True)

        self.controls_frame.pack(side=tk.TOP, fill=tk.X)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.favorites_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        settings_frame = tk.Frame(self, bg=SECONDARY_BG_COLOR)
        settings_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5, padx=10)
        tk.Label(settings_frame, text="Log Level:", bg=SECONDARY_BG_COLOR, fg=TEXT_COLOR, font=DEFAULT_FONT).pack(side=tk.LEFT)
        log_dropdown = ttk.Combobox(settings_frame, textvariable=self.log_level,
                                    values=["ALL", "INFO", "WARNING", "ERROR"], state="readonly", width=10)
        style = ttk.Style()
        style.configure("TCombobox", fieldbackground=FIELD_BG_COLOR, background=SECONDARY_BG_COLOR, foreground=TEXT_COLOR)
        style.map("TCombobox", background=[("active", WIDGET_ACTIVE_COLOR)])
        log_dropdown.pack(side=tk.LEFT, padx=5)
        log_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_logging())
        tk.Checkbutton(settings_frame, text="Verbose", variable=self.verbose, bg=SECONDARY_BG_COLOR, fg=TEXT_COLOR,
                       font=DEFAULT_FONT, selectcolor=WIDGET_ACTIVE_COLOR).pack(side=tk.LEFT)

        self.log_text.pack(fill="both", expand=True)
        self.search_frame.pack(fill="both", expand=True)
        self.update_log_display()

    def load_config(self):
        """Load logging settings from config.yml."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = yaml.safe_load(f) or {}
                self.log_level.set(config.get("log_level", "INFO"))
                self.verbose.set(config.get("verbose", False))
                level_map = {"ALL": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR}
                logging.getLogger().setLevel(level_map.get(self.log_level.get(), logging.INFO))
                logging.debug(f"Loaded config: log_level={self.log_level.get()}, verbose={self.verbose.get()}")
            except Exception as e:
                logging.error(f"Failed to load config.yml: {str(e)}", exc_info=True)

    def save_config(self):
        """Save logging settings to config.yml."""
        config = {
            "log_level": self.log_level.get(),
            "verbose": self.verbose.get()
        }
        try:
            with open(self.config_file, "w") as f:
                yaml.safe_dump(config, f)
            logging.debug(f"Saved config: {config}")
        except Exception as e:
            logging.error(f"Failed to save config.yml: {str(e)}", exc_info=True)

    def update_logging(self):
        """Update logging level and save config on change."""
        level_map = {"ALL": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR}
        logging.getLogger().setLevel(level_map.get(self.log_level.get(), logging.INFO))
        self.update_log_display()
        self.save_config()

    def on_closing(self):
        """Save config before closing."""
        self.save_config()
        self.destroy()

    def update_log_display(self):
        """Update Log tab display based on log level and verbose setting."""
        self.log_text.delete(1.0, tk.END)
        level = self.log_level.get()
        log_file = os.path.join(DECKS_DIR, "..", "logs", "app.log")
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                for line in f:
                    if level == "ALL":
                        self.log_text.insert(tk.END, line)
                    elif (level == "INFO" and any(lvl in line for lvl in ["INFO", "WARNING", "ERROR"]) or
                          level == "WARNING" and "WARNING" in line or
                          level == "ERROR" and "ERROR" in line):
                        if self.verbose.get() or "ERROR" in line or "WARNING" in line:
                            self.log_text.insert(tk.END, line)

    def show_scryfall_search(self, card_name, set_code, index):
        self.notebook.select(self.search_tab)
        self.search_frame.search_scryfall(card_name, set_code, index)