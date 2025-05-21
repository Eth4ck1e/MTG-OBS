# src/utils/cards_storage.py
import os
import json
from src.config.settings import CACHE_DIR
from fuzzywuzzy import fuzz
import logging

CARDS_JSON = os.path.join(CACHE_DIR, "cards.json")


def init_storage():
    """Initialize cards.json if it doesn't exist."""
    if not os.path.exists(CARDS_JSON):
        with open(CARDS_JSON, "w") as f:
            json.dump([], f)
        logging.info("Initialized cards.json")
    else:
        logging.debug("cards.json already exists")


def clear_storage():
    """Clear cards.json."""
    with open(CARDS_JSON, "w") as f:
        json.dump([], f)
    logging.info("Cleared cards.json")


def add_card(name, set_code, collector_number, filename):
    """Add a card to cards.json."""
    try:
        with open(CARDS_JSON, "r") as f:
            cards = json.load(f)
        logging.debug(f"Read {len(cards)} cards from cards.json")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning(f"Failed to read cards.json, starting fresh: {str(e)}")
        cards = []

    card = {
        "name": name,
        "set_code": set_code,
        "collector_number": collector_number,
        "filename": filename
    }
    if not any(c["filename"] == filename for c in cards):
        cards.append(card)
        try:
            with open(CARDS_JSON, "w") as f:
                json.dump(cards, f)
            logging.info(f"Added card to cards.json: {filename}")
        except Exception as e:
            logging.error(f"Failed to write card to cards.json: {str(e)}", exc_info=True)
    else:
        logging.debug(f"Card already exists in cards.json: {filename}")


def search_cards(query):
    """Search cards with fuzzy matching."""
    try:
        with open(CARDS_JSON, "r") as f:
            cards = json.load(f)
        logging.info(f"Searching {len(cards)} cards with query: '{query}'")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Failed to read cards.json for search: {str(e)}", exc_info=True)
        return []

    query = query.lower().strip()
    if not query:
        logging.debug("Empty query, returning all cards")
        return cards

    results = []
    for card in cards:
        score = fuzz.partial_ratio(query, card["name"].lower())
        if score >= 70:  # Threshold for fuzzy matching
            results.append(card)
            logging.debug(f"Matched card '{card['name']}' with score: {score}")
    logging.info(f"Found {len(results)} cards matching query: '{query}'")
    return results