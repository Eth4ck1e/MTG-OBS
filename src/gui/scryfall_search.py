# src/gui/scryfall_search.py
import tkinter as tk
from tkinter import ttk
import requests
import os
from PIL import Image, ImageTk
import io
import time
import json
from src.utils.image import CustomImage
from src.config.settings import CACHE_DIR, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, DECKS_DIR
import logging


class ScryfallSearchFrame(tk.Frame):
    def __init__(self, parent, browser, frame, notebook, button_width=THUMBNAIL_WIDTH, button_height=THUMBNAIL_HEIGHT,
                 padding=10):
        super().__init__(parent)
        self.browser = browser
        self.frame = frame
        self.notebook = notebook
        self.button_width = button_width
        self.button_height = button_height
        self.padding = padding
        self.results = []
        self.photos = []
        self.current_set = None
        self.create_widgets()

    def create_widgets(self):
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.search_label = tk.Label(self.search_frame, text="Search Scryfall:")
        self.search_label.pack(side=tk.LEFT, padx=self.padding)
        self.search_entry = tk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=self.padding)
        self.search_entry.bind("<Return>", self.handle_enter)
        self.search_button = tk.Button(self.search_frame, text="Search", command=self.manual_search)
        self.search_button.pack(side=tk.LEFT, padx=self.padding)

        self.status_label = tk.Label(self, text="Enter a card name above to search Scryfall.")
        self.status_label.pack(side=tk.TOP, pady=5)

        self.sidebar = tk.Frame(self, width=200, bg="lightgray")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.results_frame = tk.Frame(self)
        self.results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.sets_label = tk.Label(self.sidebar, text="Sets:", bg="lightgray")
        self.sets_label.pack(side=tk.TOP, pady=5)
        self.sets_listbox = tk.Listbox(self.sidebar, height=20)
        self.sets_listbox.pack(side=tk.TOP, fill=tk.Y, expand=True)
        self.sets_listbox.bind("<<ListboxSelect>>", self.filter_by_set)

    def handle_enter(self, event):
        """Handle Enter key press, only search if Scryfall tab is active."""
        current_tab = self.notebook.index('current')
        scryfall_tab_index = self.notebook.index(self.master)
        logging.debug(f"Enter pressed: Current tab index={current_tab}, Scryfall tab index={scryfall_tab_index}")
        if current_tab == scryfall_tab_index:
            logging.debug("Scryfall tab active, triggering manual search")
            self.manual_search()
        else:
            logging.debug("Enter ignored—Scryfall tab not active")

    def manual_search(self):
        """Perform a manual Scryfall search from the entry field."""
        card_name = self.search_entry.get().strip()
        if not card_name:
            logging.warning("Search canceled: No card name entered")
            self.status_label.config(text="Please enter a card name to search.")
            return
        self.search_scryfall(card_name, None, None)

    def search_scryfall(self, card_name, set_code, index):
        clean_name = card_name.replace("_", " ").strip()
        self.status_label.config(text=f"Searching for '{clean_name}' across all sets...")
        self.results = []
        self.photos = []
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.sets_listbox.delete(0, tk.END)

        url = f"https://api.scryfall.com/cards/search?q=\"{clean_name}\" unique:prints"
        logging.debug(f"Searching Scryfall with URL: {url}")
        try:
            while url:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                if "data" in data:
                    self.results.extend(data["data"])
                    if "next_page" in data:
                        url = data["next_page"]
                        logging.debug(f"Fetching next page: {url}")
                        time.sleep(0.1)
                    else:
                        url = None
                else:
                    logging.info(f"No results found for '{clean_name}' in Scryfall response")
                    self.status_label.config(text=f"No results found for '{clean_name}'.")
                    return
            logging.debug(f"Total results fetched: {len(self.results)}")
            if self.results:
                self.display_results(clean_name, set_code, index)
                self.populate_sets()
            else:
                logging.info(f"No printings found for '{clean_name}'")
                self.status_label.config(text=f"No printings found for '{clean_name}'.")
        except requests.RequestException as e:
            logging.error(f"Scryfall search failed for '{clean_name}': {str(e)}", exc_info=True)
            self.status_label.config(text="Search failed. Check logs.")

    def populate_sets(self):
        sets = sorted(set(card["set"] for card in self.results))
        self.sets_listbox.insert(0, "All Sets")
        for set_code in sets:
            self.sets_listbox.insert(tk.END, set_code)
        logging.debug(f"Populated sets: {sets}")

    def filter_by_set(self, event):
        selection = self.sets_listbox.curselection()
        if not selection:
            return
        set_code = self.sets_listbox.get(selection[0])
        self.current_set = None if set_code == "All Sets" else set_code
        self.display_results(self.card_name, self.set_code, self.index)

    def display_results(self, card_name, set_code, index):
        self.card_name = card_name
        self.set_code = set_code
        self.index = index
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        filtered_results = [card for card in self.results if not self.current_set or card["set"] == self.current_set]
        self.status_label.config(text=f"Found {len(filtered_results)} versions for '{card_name}':")

        for i, card in enumerate(filtered_results):
            if "image_uris" in card and "small" in card["image_uris"]:
                small_image_url = card["image_uris"]["small"]
                high_quality_url = card["image_uris"]["png"]
                frame = tk.Frame(self.results_frame)
                frame.pack(side=tk.TOP, fill=tk.X, pady=2)

                try:
                    response = requests.get(small_image_url)
                    response.raise_for_status()
                    img_data = response.content
                    img = Image.open(io.BytesIO(img_data))
                    img = img.resize((self.button_width // 2, self.button_height // 2), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.photos.append(photo)
                    img_label = tk.Label(frame, image=photo)
                    img_label.pack(side=tk.LEFT, padx=self.padding)
                except Exception as e:
                    logging.warning(f"Failed to load thumbnail for {card['name']}: {str(e)}")
                    img_label = tk.Label(frame, text="[Image Failed]")
                    img_label.pack(side=tk.LEFT, padx=self.padding)

                info = f"{card['name']} ({card['set'].upper()} #{card['collector_number']})"
                if "foil" in card and card["foil"]:
                    info += " [Foil]"
                if "nonfoil" in card and not card["nonfoil"]:
                    info += " [Foil Only]"
                if card.get("frame_effects"):
                    info += f" [{', '.join(card['frame_effects'])}]"
                label = tk.Label(frame, text=info)
                label.pack(side=tk.LEFT, padx=self.padding)

                # Add to Deck button
                add_button = tk.Button(frame, text="Add to Deck",
                                       command=lambda url=high_quality_url,
                                                      fname=f"{card['name'].replace(' ', '_')}_{card['set']}_{card['collector_number']}.png",
                                                      set=card['set'], num=card['collector_number']:
                                       self.add_to_deck(url, fname, card['name'], set, num))
                add_button.pack(side=tk.RIGHT, padx=self.padding)

                # Select button for replacement (only if index provided)
                if self.index is not None:
                    parts = self.frame.images[self.index].name.rsplit("_", 2)
                    old_collector_number = parts[2].replace(".png", "")
                    button = tk.Button(frame, text="Select",
                                       command=lambda url=high_quality_url,
                                                      fname=f"{card['name'].replace(' ', '_')}_{card['set']}_{card['collector_number']}.png",
                                                      idx=self.index,
                                                      old_set=self.set_code, old_num=old_collector_number,
                                                      new_set=card['set'], new_num=card['collector_number']:
                                       self.replace_card(url, fname, idx, old_set, old_num, new_set, new_num))
                    button.pack(side=tk.RIGHT, padx=self.padding)
            else:
                logging.warning(f"No image available for {card['name']} ({card['set']} #{card['collector_number']})")

    def add_to_deck(self, image_url, filename, card_name, set_code, collector_number):
        """Add a card from search results to scryfall_added.txt and cache."""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_path = os.path.join(CACHE_DIR, filename)
            with open(image_path, "wb") as f:
                f.write(response.content)
            logging.debug(f"Downloaded {filename} to cache")

            added_file = os.path.join(DECKS_DIR, "scryfall_added.txt")
            entry = f"1x {card_name} ({set_code}) {collector_number} []\n"
            with open(added_file, "a") as f:
                f.write(entry)
            logging.debug(f"Added {card_name} ({set_code} #{collector_number}) to scryfall_added.txt")

            cache_file = os.path.join(CACHE_DIR, "deck_cache.json")
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, "r") as f:
                        cache_data = json.load(f)
                    cached_files = cache_data.get("files", [])
                    if filename not in cached_files:
                        cached_files.append(filename)
                        cache_data["files"] = cached_files
                        with open(cache_file, "w") as f:
                            json.dump(cache_data, f)
                        logging.debug(f"Updated deck_cache.json with {filename}")
                except (json.JSONDecodeError, OSError) as e:
                    logging.warning(f"Failed to update deck_cache.json: {str(e)}")

            self.frame.reload_images()
            logging.info(f"Added {card_name} to decks")
            self.status_label.config(text=f"Added {card_name} to decks. Search again or add another.")
        except Exception as e:
            logging.error(f"Failed to add card to deck: {str(e)}", exc_info=True)
            self.status_label.config(text=f"Failed to add {card_name} to deck. Check logs.")

    def replace_card(self, image_url, filename, index, old_set_code, old_collector_number, new_set_code,
                     new_collector_number):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_path = os.path.join(CACHE_DIR, filename)
            with open(image_path, "wb") as f:
                f.write(response.content)
            new_image = CustomImage(CACHE_DIR, filename)
            new_image.load_thumbnail(self.button_width, self.button_height)
            self.frame.images[index] = new_image
            self.frame.create_grid_of_buttons(target_frame=self.frame.image_frame, show_fav_button=True)

            success = self.frame.deck_parser.update_card(
                self.card_name, old_set_code, old_collector_number,
                new_set_code, new_collector_number
            )

            cache_file = os.path.join(CACHE_DIR, "deck_cache.json")
            cache_updated = False
            old_filename = f"{self.card_name.replace(' ', '_')}_{old_set_code}_{old_collector_number}.png"
            old_image_path = os.path.join(CACHE_DIR, old_filename)

            if os.path.exists(old_image_path):
                is_used = False
                for _, line in self.frame.deck_parser.get_deck_lines():
                    if old_filename.replace(".png", "") in line:
                        is_used = True
                        break
                if not is_used:
                    try:
                        os.remove(old_image_path)
                        logging.debug(f"Removed unused image from cache: {old_filename}")
                    except OSError as e:
                        logging.warning(f"Failed to remove unused image {old_filename}: {str(e)}")

            if os.path.exists(cache_file):
                try:
                    with open(cache_file, "r") as f:
                        cache_data = json.load(f)
                    cached_files = cache_data.get("files", [])
                    if old_filename in cached_files:
                        cached_files.remove(old_filename)
                        logging.debug(f"Removed {old_filename} from deck_cache.json")
                    if filename not in cached_files:
                        cached_files.append(filename)
                        logging.debug(f"Added {filename} to deck_cache.json")
                    cache_data["files"] = cached_files
                    with open(cache_file, "w") as f:
                        json.dump(cache_data, f)
                    cache_updated = True
                except (json.JSONDecodeError, OSError) as e:
                    logging.warning(f"Failed to update deck_cache.json: {str(e)}")

            if success and cache_updated:
                logging.info(f"Replaced card with {filename}, updated deck list, and cleaned cache")
                self.status_label.config(text="Card replaced. Select another or search again.")
            elif success:
                logging.info(f"Replaced card with {filename} and updated deck list (cache update failed)")
                self.status_label.config(text="Card replaced (cache update failed). Select another or search again.")
            else:
                logging.error(
                    f"Failed to update deck list: {self.card_name} ({old_set_code} #{old_collector_number}) to ({new_set_code} #{new_collector_number})")
                self.status_label.config(text="Failed to update deck list. Check logs.")
        except requests.RequestException as e:
            logging.error(f"Failed to download image: {str(e)}", exc_info=True)
            self.status_label.config(text="Failed to replace card. Check logs.")