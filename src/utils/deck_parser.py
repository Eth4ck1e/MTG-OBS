# src/utils/deck_parser.py
import os
import re
from src.config.settings import DECKS_DIR
import logging

class DeckParser:
    def __init__(self):
        self.pattern = re.compile(r"(\d+)x (.+?) \((.+?)\) ([0-9A-Za-z-]+)(?: \*[FE]\*)? \[(.*?)(?:\{.*?\})?(?:,.*)?\]")
        self.refresh_deck_files()

    def refresh_deck_files(self):
        """Refresh the list of deck files from DECKS_DIR."""
        try:
            self.deck_files = [
                f for f in os.listdir(DECKS_DIR)
                if os.path.isfile(os.path.join(DECKS_DIR, f)) and f.endswith(".txt") and f != "favorites.txt"
            ]
            logging.debug(f"Refreshed deck files: {self.deck_files}")
        except FileNotFoundError:
            self.deck_files = []
            logging.warning(f"DECKS_DIR not found: {DECKS_DIR}")

    def get_deck_lines(self):
        """Return all lines from deck files with file info."""
        deck_lines = []
        for deck_file in self.deck_files:
            with open(os.path.join(DECKS_DIR, deck_file), "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                deck_lines.append((deck_file, line.strip()))
        return deck_lines

    def update_card(self, old_card_name, old_set_code, old_collector_number, new_set_code, new_collector_number):
        """Update a card in the deck file with new set and collector number."""
        for deck_file in self.deck_files:
            file_path = os.path.join(DECKS_DIR, deck_file)
            with open(file_path, "r") as f:
                lines = f.readlines()
            updated = False
            for i, line in enumerate(lines):
                match = self.pattern.match(line.strip())
                if match:
                    quantity, card_name, set_code, collector_number, card_type = match.groups()
                    if (card_name == old_card_name and
                        set_code == old_set_code and
                        collector_number == old_collector_number):
                        foil_marker = " *F*" if "*F*" in line else " *E*" if "*E*" in line else ""
                        tags = line[line.find('['):].strip()
                        new_line = f"{quantity}x {card_name} ({new_set_code}) {new_collector_number}{foil_marker} {tags}\n"
                        lines[i] = new_line
                        updated = True
                        logging.debug(f"Updated {deck_file}: {line.strip()} -> {new_line.strip()}")
                        break
                if updated:
                    break
            if updated:
                with open(file_path, "w") as f:
                    f.writelines(lines)
                return True
        logging.warning(f"Card {old_card_name} ({old_set_code} #{old_collector_number}) not found in any deck file.")
        return False