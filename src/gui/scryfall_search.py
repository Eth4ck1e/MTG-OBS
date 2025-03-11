# src/gui/scryfall_search.py
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
from PIL import Image, ImageTk
import io
import time
from src.utils.image import CustomImage
from src.config.settings import CACHE_DIR, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT
import logging


class ScryfallSearchFrame(tk.Frame):
    def __init__(self, parent, browser, frame, button_width=THUMBNAIL_WIDTH, button_height=THUMBNAIL_HEIGHT,
                 padding=10):
        super().__init__(parent)
        self.browser = browser
        self.frame = frame
        self.button_width = button_width
        self.button_height = button_height
        self.padding = padding
        self.results = []
        self.photos = []
        self.current_set = None
        self.create_widgets()

    def create_widgets(self):
        self.search_label = tk.Label(self, text="Searching Scryfall...")
        self.search_label.pack(side=tk.TOP, pady=5)

        self.sidebar = tk.Frame(self, width=200, bg="lightgray")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.results_frame = tk.Frame(self)
        self.results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.sets_label = tk.Label(self.sidebar, text="Sets:", bg="lightgray")
        self.sets_label.pack(side=tk.TOP, pady=5)
        self.sets_listbox = tk.Listbox(self.sidebar, height=20)
        self.sets_listbox.pack(side=tk.TOP, fill=tk.Y, expand=True)
        self.sets_listbox.bind("<<ListboxSelect>>", self.filter_by_set)

    def search_scryfall(self, card_name, set_code, index):
        clean_name = card_name.replace("_", " ").strip()
        self.search_label.config(text=f"Searching for '{clean_name}' across all sets...")
        self.results = []
        self.photos = []
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.sets_listbox.delete(0, tk.END)

        url = f"https://api.scryfall.com/cards/search?q=\"{clean_name}\""
        logging.debug(f"Initial search URL: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if "data" not in data or not data["data"]:
                self.search_label.config(text=f"No results found for '{clean_name}'.")
                logging.warning(f"No initial results for '{clean_name}'")
                return
            oracle_id = data["data"][0]["oracle_id"]
            logging.debug(f"Found oracle_id: {oracle_id}")
        except requests.RequestException as e:
            logging.error(f"Initial Scryfall search failed: {str(e)}")
            self.search_label.config(text="Search failed. Check logs.")
            return

        prints_url = f"https://api.scryfall.com/cards/search?order=released&q=oracleid:{oracle_id}&unique=prints"
        logging.debug(f"Fetching all prints with URL: {prints_url}")
        try:
            while prints_url:
                response = requests.get(prints_url)
                response.raise_for_status()
                data = response.json()
                logging.debug(
                    f"Prints response: total_cards={data.get('total_cards', 0)}, has_more={data.get('has_more', False)}")
                if "data" in data:
                    self.results.extend(data["data"])
                    if "next_page" in data:
                        prints_url = data["next_page"]
                        logging.debug(f"Fetching next page: {prints_url}")
                        time.sleep(0.1)
                    else:
                        prints_url = None
                else:
                    logging.warning("No 'data' in prints response, breaking loop")
                    break
            logging.debug(f"Total printings fetched: {len(self.results)}")
            if self.results:
                self.display_results(clean_name, set_code, index)
                self.populate_sets()
            else:
                self.search_label.config(text=f"No printings found for '{clean_name}'.")
                logging.warning(f"No printings returned for oracle_id: {oracle_id}")
        except requests.RequestException as e:
            logging.error(f"Prints search failed: {str(e)}")
            self.search_label.config(text="Search failed. Check logs.")

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
        self.search_label.config(text=f"Found {len(filtered_results)} versions for '{card_name}':")

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
                filename = f"{card_name.replace(' ', '_')}_{card['set']}_{card['collector_number']}.png"
                parts = self.frame.images[index].name.rsplit("_", 2)
                old_collector_number = parts[2].replace(".png", "")
                button = tk.Button(frame, text="Select",
                                   command=lambda url=high_quality_url, fname=filename, idx=index,
                                                  old_set=self.set_code, old_num=old_collector_number,
                                                  new_set=card['set'], new_num=card['collector_number']:
                                   self.replace_card(url, fname, idx, old_set, old_num, new_set, new_num))
                button.pack(side=tk.RIGHT, padx=self.padding)
            else:
                logging.warning(f"No image available for {card['name']} ({card['set']} #{card['collector_number']})")

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
            if success:
                messagebox.showinfo("Success", f"Replaced card with {filename} and updated deck list.")
            else:
                logging.error(
                    f"Failed to update deck list: {self.card_name} ({old_set_code} #{old_collector_number}) to ({new_set_code} #{new_collector_number})")
                messagebox.showwarning("Partial Success",
                                       f"Replaced card with {filename}, but failed to update deck list. Check logs.")
            self.search_label.config(text="Card replaced. Select another or close tab.")
        except requests.RequestException as e:
            logging.error(f"Failed to download image: {str(e)}")
            messagebox.showerror("Error", "Failed to replace card. Check logs.")