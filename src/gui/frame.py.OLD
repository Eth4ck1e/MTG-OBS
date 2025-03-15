# src/gui/frame.py
import os
import json
import tkinter as tk
from tkinter import ttk, filedialog
from src.utils.image import CustomImage, download_scryfall_images, create_clear_png  # Add create_clear_png
from src.utils.paths import get_relative_path
from src.utils.favorites import save_favorite, load_favorites
from src.utils.deck_parser import DeckParser
from src.config.settings import THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, CACHE_DIR, DECKS_DIR  # Remove OUTPUT_DIR
import logging
import shutil
import threading


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
        self.filter_timer = None  # For debouncing

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
            menu = tk.Menu(label, tearoff=0)
            menu.add_command(label="Replace Card", command=lambda i=index: self.replace_card(i))
            label.bind("<Button-3>", lambda e, m=menu: m.tk_popup(e.x_root, e.y_root))
            self.list_of_buttons.append((label, label_name))
            label.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
        logging.debug(f"Created {len(self.list_of_buttons)} buttons")

    def set_slot(self, slot, filename):
        path = get_relative_path(CACHE_DIR, filename)
        from PIL import Image  # Already at top
        try:
            with Image.open(path) as img:
                width, height = img.size
                logging.debug(f"Setting slot {slot} to {path} (size: {width}x{height}px)")
        except Exception as e:
            logging.warning(f"Could not check image size for {path}: {str(e)}")

        clear_url = create_clear_png()  # Get base64 clear.png
        if slot == 0:  # Slot 1: Push current slot 1 to slot 2
            current_slot1 = self.browser.get_slot(0)
            if current_slot1 and current_slot1 != clear_url:  # Compare to base64 string
                logging.debug(f"Pushing slot 1 ({current_slot1}) to slot 2")
                self.browser.set_slot(1, current_slot1)
            self.browser.set_slot(0, path)
        elif slot == 1:  # Slot 2: Replace directly
            self.browser.set_slot(1, path)
        else:
            logging.warning(f"Invalid slot index: {slot}")
            return
        # No write_html—Flask updates live

    def filter_cards(self, event=None):
        """Schedule filtering with a debounce delay."""
        if not hasattr(self, 'search_field'):
            print("No search field in this frame")
            return
        if self.filter_timer:
            self.after_cancel(self.filter_timer)
        self.filter_timer = self.after(300, self._do_filter)

    def _do_filter(self):
        """Perform the actual filtering after debounce delay."""
        search_text = self.search_field.get().lower()
        print(f"Filtering with text: {search_text}")
        for label, _ in self.list_of_buttons:
            label.pack_forget()
        visible_count = 0
        for label, name_label in self.list_of_buttons:
            card_name = name_label["text"].lower()
            if not search_text or search_text in card_name:
                label.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
                visible_count += 1
        self.image_frame.update_idletasks()
        logging.debug(f"Filtered cards, visible: {visible_count}")


class Frame(BaseCardFrame):
    def __init__(self, parent, browser, favorites_frame, window, button_width=THUMBNAIL_WIDTH,
                 button_height=THUMBNAIL_HEIGHT, padding=10):
        super().__init__(parent, browser, button_width, button_height, padding)
        self.favorites_frame = favorites_frame
        self.window = window
        self.deck_parser = DeckParser()
        self.frame_buttons = tk.Frame(self, bg="lightgray")
        self.search_field = tk.Entry(self.frame_buttons, width=50)
        self.image_frame = tk.Frame(self, bg="white")
        self.failures = []
        self.create_widgets()
        self.load_all_decks()

    def create_widgets(self):
        print("Creating widgets in Frame")
        self.frame_buttons.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        reload_button = tk.Button(self.frame_buttons, text="Reload", command=self.reload_images, width=10)
        reload_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
        clear_button = tk.Button(self.frame_buttons, text="Clear All", command=self.clear_all, width=10)
        clear_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
        add_deck_button = tk.Button(self.frame_buttons, text="Add Deck", command=self.add_deck, width=10)
        add_deck_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
        search_label = tk.Label(self.frame_buttons, text="Search:")
        search_label.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
        self.search_field.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
        self.search_field.bind("<KeyRelease>", self.filter_cards)
        print("Search field packed")
        self.image_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        print("Image frame packed")
        self.update()

    def add_to_favorites(self, index):
        card = self.images[index]
        self.favorites_frame.add_card(card)
        save_favorite(card.name)

    def clear_all(self):
        """Clear all deck files, cached images, and reset the app."""
        if not tk.messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all decks and images?"):
            logging.info("Clear all operation canceled by user")
            return
        try:
            for file in os.listdir(DECKS_DIR):
                if file.endswith('.txt'):
                    os.remove(os.path.join(DECKS_DIR, file))
                    logging.debug(f"Deleted deck file: {file}")
            if os.path.exists(CACHE_DIR):
                shutil.rmtree(CACHE_DIR)
                logging.debug("Cleared cache directory")
            os.makedirs(CACHE_DIR, exist_ok=True)
            self.images = []
            self.list_of_buttons = []
            self.create_grid_of_buttons(target_frame=self.image_frame, show_fav_button=True)
            self.favorites_frame.load_favorites()
            self.update_idletasks()
            logging.info("All decks and images cleared successfully")
        except Exception as e:
            logging.error(f"Failed to clear all: {str(e)}", exc_info=True)

    def add_deck(self):
        """Open file browser to add a deck file and reload."""
        file_path = filedialog.askopenfilename(
            title="Select Deck File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if not file_path:
            logging.info("Deck addition canceled by user")
            return
        try:
            dest_path = os.path.join(DECKS_DIR, os.path.basename(file_path))
            if os.path.exists(dest_path):
                raise FileExistsError(f"File {os.path.basename(file_path)} already exists in decks directory")
            shutil.copy(file_path, dest_path)
            logging.info(f"Added deck file: {dest_path}")
            self.reload_images()
        except Exception as e:
            logging.error(f"Failed to add deck: {str(e)}", exc_info=True)

    def _download_images_thread(self, cards_to_fetch):
        """Download images in a separate thread."""
        download_scryfall_images(cards_to_fetch)

    def _update_progress(self, progress_bar, expected_files):
        """Poll the cache directory for file count and update progress."""
        current_files = len([f for f in os.listdir(CACHE_DIR) if f.endswith('.png')])
        logging.debug(f"Progress: {current_files}/{expected_files} files downloaded")
        progress_bar["value"] = current_files
        self.update_idletasks()

        if current_files < expected_files or not self.download_thread.is_alive():
            self.after(100, self._update_progress, progress_bar, expected_files)
        else:
            self._finalize_load(progress_bar)

    def _finalize_load(self, progress_bar):
        """Complete the loading process after downloads."""
        progress_bar.destroy()
        downloaded_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.png')]
        logging.debug(f"Finalizing load with {len(downloaded_files)} downloaded files")
        for filename in downloaded_files:
            image_path = os.path.join(CACHE_DIR, filename)
            image = CustomImage(CACHE_DIR, filename)
            image.load_thumbnail(self.button_width, self.button_height)
            self.images.append(image)
            self.cached_files.append(filename)
        if not self.images:
            logging.warning("No images loaded despite files in cache")
            logging.info("No valid cards found in deck files")
        else:
            self.create_grid_of_buttons(target_frame=self.image_frame, show_fav_button=True)
            with open(os.path.join(CACHE_DIR, "deck_cache.json"), "w") as f:
                json.dump({"mtime": self.deck_mtime, "files": self.cached_files}, f)
            if self.failures:
                logging.warning(
                    f"Loaded {len(self.images)} cards with failures: {', '.join(self.failures[:10])}{'...' if len(self.failures) > 10 else ''}")
            else:
                logging.info(f"Loaded {len(self.images)} cards successfully")

    def load_all_decks(self):
        self.images = []
        self.failures = []
        os.makedirs(DECKS_DIR, exist_ok=True)
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.deck_parser.refresh_deck_files()
        deck_files = self.deck_parser.deck_files
        if not deck_files:
            logging.info("No deck files found in the 'decks' directory")
            return

        cache_file = os.path.join(CACHE_DIR, "deck_cache.json")
        self.deck_mtime = max(os.path.getmtime(os.path.join(DECKS_DIR, f)) for f in deck_files) if deck_files else 0

        progress_bar = ttk.Progressbar(orient=tk.HORIZONTAL, length=200, mode='determinate')
        progress_bar.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
            if cache_data.get("mtime", 0) >= self.deck_mtime:
                cached_files = cache_data["files"]
                progress_bar["maximum"] = len(cached_files)
                for i, filename in enumerate(cached_files):
                    image_path = os.path.join(CACHE_DIR, filename)
                    if os.path.exists(image_path):
                        image = CustomImage(CACHE_DIR, filename)
                        image.load_thumbnail(self.button_width, self.button_height)
                        self.images.append(image)
                    progress_bar["value"] = i + 1
                    self.update_idletasks()
                if self.images:
                    progress_bar.destroy()
                    self.create_grid_of_buttons(target_frame=self.image_frame, show_fav_button=True)
                    logging.info(f"Loaded {len(self.images)} cards from cache")
                    return
                else:
                    progress_bar.destroy()
                    logging.info("Cache found but no images loaded. Reparsing decks")

        unique_cards = set()
        self.cached_files = []
        cards_to_fetch = []
        for deck_file, line in self.deck_parser.get_deck_lines():
            match = self.deck_parser.pattern.match(line)
            if match:
                quantity, card_name, set_code, collector_number, card_type = match.groups()
                is_foil = "*F*" in line or "*E*" in line
                card_id = f"{card_name}_{set_code}_{collector_number}"
                if card_id not in unique_cards:
                    unique_cards.add(card_id)
                    cards_to_fetch.append({
                        "card_name": card_name,
                        "set_code": set_code,
                        "collector_number": collector_number,
                        "is_foil": is_foil
                    })
            else:
                logging.warning(f"Failed to parse line in {deck_file}: {line}")
                self.failures.append(f"Unparsed: {line}")

        expected_files = len(cards_to_fetch)
        if expected_files == 0:
            progress_bar.destroy()
            logging.info("No valid cards found in deck files")
            return

        progress_bar["maximum"] = expected_files
        progress_bar["value"] = 0
        self.update_idletasks()

        self.download_thread = threading.Thread(target=self._download_images_thread, args=(cards_to_fetch,))
        self.download_thread.start()
        self.after(100, self._update_progress, progress_bar, expected_files)

    def reload_images(self):
        self.load_all_decks()

    def replace_card(self, index):
        filename = self.images[index].name
        parts = filename.rsplit("_", 2)
        card_name = " ".join(parts[0].split("_"))
        set_code = parts[1]
        self.window.show_scryfall_search(card_name, set_code, index)


class FavoritesFrame(BaseCardFrame):
    def __init__(self, parent, browser, button_width=THUMBNAIL_WIDTH, button_height=THUMBNAIL_HEIGHT, padding=10):
        super().__init__(parent, browser, button_width, button_height, padding)
        self.config(borderwidth=2, relief="groove")
        self.load_favorites()

    def load_favorites(self):
        """Load favorites from file on startup."""
        self.images = load_favorites(self.button_width, self.button_height)
        self.create_grid_of_buttons(show_fav_button=False)

    def add_card(self, card):
        """Add a card to the favorites frame."""
        if card.name not in [img.name for img in self.images]:
            self.images.append(card)
            self.create_grid_of_buttons(show_fav_button=False)