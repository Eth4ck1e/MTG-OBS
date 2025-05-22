# src/web/app_server.py
import os
import json
import shutil
from flask import Flask, send_from_directory, jsonify, request
from src.config.settings import CACHE_DIR, DECKS_DIR, OUTPUT_DIR, LOGS_DIR
from src.utils.image import create_clear_png, CustomImage, download_scryfall_images
from src.utils.favorites import save_favorite, load_favorites
from src.utils.deck_parser import DeckParser
from src.web.obs_html import write_obs_html
import logging
import threading

app = Flask(__name__)

# In-memory card data
card_data = []

def load_deck_cards():
    """Load cards from deck files and cache, using deck_cache.json if available."""
    global card_data
    deck_parser = DeckParser()
    deck_parser.refresh_deck_files()
    deck_files = deck_parser.deck_files
    cache_file = os.path.join(CACHE_DIR, "deck_cache.json")
    card_data = []

    # Check cache first
    if os.path.exists(CACHE_DIR):
        cached_files = []
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cache_data = json.load(f)
                deck_mtime = max(os.path.getmtime(os.path.join(DECKS_DIR, f)) for f in deck_files) if deck_files else 0
                if cache_data.get("mtime", 0) >= deck_mtime:
                    cached_files = cache_data.get("files", [])
                    logging.info(f"Using deck_cache.json with {len(cached_files)} files")
            except Exception as e:
                logging.warning(f"Failed to read deck_cache.json: {str(e)}")

        # Load existing images from cache
        for filename in cached_files:
            if filename.endswith('.png') and os.path.exists(os.path.join(CACHE_DIR, filename)):
                name = " ".join(filename.replace("_", " ").split(" ")[0:-2])
                card_data.append({'name': name, 'filename': filename})
                logging.debug(f"Loaded cached image: {filename}")

    if not deck_files:
        logging.info("No deck files found in the 'decks' directory")
        return card_data

    # Parse deck files for new cards
    unique_cards = set()
    cards_to_fetch = []
    for deck_file, line in deck_parser.get_deck_lines():
        match = deck_parser.pattern.match(line)
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

    if not cards_to_fetch:
        logging.info("No new cards to fetch")
        return card_data

    # Download new images
    image_paths = download_scryfall_images(cards_to_fetch)
    new_files = []
    for path in image_paths:
        if os.path.exists(path):
            filename = os.path.basename(path)
            if filename not in [card['filename'] for card in card_data]:
                name = " ".join(filename.replace("_", " ").split(" ")[0:-2])
                card_data.append({'name': name, 'filename': filename})
                new_files.append(filename)
                logging.debug(f"Added new image: {filename}")

    # Update deck_cache.json
    try:
        deck_mtime = max(os.path.getmtime(os.path.join(DECKS_DIR, f)) for f in deck_files) if deck_files else 0
        with open(cache_file, "w") as f:
            json.dump({"mtime": deck_mtime, "files": [card['filename'] for card in card_data]}, f)
        logging.info(f"Updated deck_cache.json with {len(card_data)} files")
    except Exception as e:
        logging.warning(f"Failed to write deck_cache.json: {str(e)}")

    logging.info(f"Loaded {len(card_data)} cards from decks and cache")
    return card_data

@app.route('/cache/images/<filename>')
def cache_images(filename):
    """Serve files from cache/images directory."""
    try:
        logging.debug(f"Serving image: {filename} from {CACHE_DIR}")
        return send_from_directory(CACHE_DIR, filename)
    except Exception as e:
        logging.error(f"Failed to serve image {filename}: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Image not found'}), 404

@app.route('/obs/<path:filename>')
def serve_obs_file(filename):
    """Serve OBS files from output/obs."""
    try:
        file_path = os.path.normpath(os.path.join(OUTPUT_DIR, "obs", filename))
        logging.debug(f"Serving OBS file: {filename} from {file_path}")
        if not os.path.exists(file_path):
            logging.error(f"OBS file not found: {file_path}")
            return jsonify({'status': 'error', 'message': f'File {filename} not found'}), 404
        return send_from_directory(os.path.join(OUTPUT_DIR, "obs"), filename)
    except Exception as e:
        logging.error(f"Failed to serve OBS file {filename}: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to load file: {str(e)}'}), 500

@app.route('/app.js')
def serve_app_js():
    """Serve app.js from output."""
    try:
        file_path = os.path.normpath(os.path.join(OUTPUT_DIR, "app.js"))
        logging.debug(f"Serving app.js from {file_path}")
        if not os.path.exists(file_path):
            logging.error(f"app.js not found at {file_path}")
            return jsonify({'status': 'error', 'message': 'app.js not found'}), 404
        return send_from_directory(OUTPUT_DIR, "app.js")
    except Exception as e:
        logging.error(f"Failed to serve app.js: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to load app.js: {str(e)}'}), 500

@app.route('/')
def index(browser):
    """Serve the App UI."""
    try:
        app_html_path = os.path.normpath(os.path.join(OUTPUT_DIR, "index.html"))
        logging.info(f"Serving app index.html from {app_html_path}")
        if not os.path.exists(app_html_path):
            logging.error(f"App index.html not found at {app_html_path}")
            return jsonify({'status': 'error', 'message': 'App HTML not found'}), 404
        return send_from_directory(OUTPUT_DIR, "index.html")
    except Exception as e:
        logging.error(f"Error serving app index.html: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Failed to load app'}), 500

@app.route('/obs')
def obs_page(browser):
    """Serve the OBS slot display page."""
    try:
        write_obs_html(browser)
        obs_html_path = os.path.normpath(os.path.join(OUTPUT_DIR, "obs", "index.html"))
        logging.info(f"Serving OBS index.html from {obs_html_path}")
        if not os.path.exists(obs_html_path):
            logging.error(f"OBS index.html not found at {obs_html_path}")
            return jsonify({'status': 'error', 'message': 'OBS HTML not found'}), 404
        return send_from_directory(os.path.join(OUTPUT_DIR, "obs"), "index.html")
    except Exception as e:
        logging.error(f"Error in OBS index route: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Failed to load OBS page'}), 500

@app.route('/cards')
def get_cards():
    """Return card data, filtered by search query if provided."""
    try:
        search = request.args.get('search', '').lower()
        cards = card_data
        if search:
            cards = [card for card in cards if search in card['name'].lower()]
        if not cards:
            logging.warning("No cards available")
        logging.info(f"Returning {len(cards)} cards for search: {search}")
        return jsonify(cards)
    except Exception as e:
        logging.error(f"Error in get_cards: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Failed to load cards'}), 500

@app.route('/favorites')
def get_favorites():
    """Return favorite cards."""
    try:
        favorites = load_favorites(200, 280)
        logging.info(f"Loaded {len(favorites)} favorite cards")
        return jsonify([{'name': img.name, 'filename': img.name} for img in favorites])
    except Exception as e:
        logging.error(f"Error in get_favorites: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/card_action', methods=['POST'])
def card_action(browser):
    """Handle card actions."""
    try:
        data = request.json
        type_ = data.get('type')
        index = data.get('index')
        source = data.get('source', 'cards')
        cards = card_data if source == 'cards' else [{'name': img.name, 'filename': img.name} for img in load_favorites(200, 280)]
        if index >= len(cards):
            logging.error(f"Invalid card index: {index}, source: {source}")
            return jsonify({'status': 'error', 'message': 'Invalid index'}), 400
        card = cards[index]
        if type_ == 'fav':
            save_favorite(card['filename'])
            logging.info(f"Added {card['filename']} to favorites")
        elif type_ == 'slot1':
            path = os.path.join(CACHE_DIR, card['filename'])
            current_slot1 = browser.get_slot(0)
            clear_url = create_clear_png()
            if current_slot1 and current_slot1 != clear_url:
                browser.set_slot(1, current_slot1)
            browser.set_slot(0, path)
            logging.info(f"Set slot 1 to {card['filename']}")
        elif type_ == 'slot2':
            path = os.path.join(CACHE_DIR, card['filename'])
            browser.set_slot(1, path)
            logging.info(f"Set slot 2 to {card['filename']}")
        elif type_ == 'replace':
            logging.warning("Replace card not yet implemented")
            return jsonify({'status': 'error', 'message': 'Replace card not yet implemented'}), 501
        write_obs_html(browser)
        return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Error in card action {type_}: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/deck_action', methods=['POST'])
def deck_action():
    """Handle deck actions."""
    global card_data
    try:
        logging.debug(f"Received deck_action request: {request.form}")
        if 'deck_file' in request.files:  # Add deck
            file = request.files['deck_file']
            if not file or not file.filename:
                logging.warning("No deck file provided or empty filename")
                return jsonify({'status': 'error', 'message': 'No file provided'}), 400
            dest_path = os.path.join(DECKS_DIR, file.filename)
            if os.path.exists(dest_path):
                logging.warning(f"Deck file already exists: {file.filename}")
                return jsonify({'status': 'error', 'message': 'File already exists'}), 400
            file.save(dest_path)
            logging.info(f"Added deck file: {dest_path}")
            card_data = load_deck_cards()
            return jsonify({'status': 'success'})
        action = request.form.get('action') or (request.json.get('action') if request.json else None)
        if action == 'reload':
            card_data = load_deck_cards()
            logging.info("Reloaded deck cards")
            return jsonify({'status': 'success'})
        elif action == 'clear':
            for file in os.listdir(DECKS_DIR):
                if file.endswith('.txt'):
                    os.remove(os.path.join(DECKS_DIR, file))
                    logging.debug(f"Deleted deck file: {file}")
            if os.path.exists(CACHE_DIR):
                shutil.rmtree(CACHE_DIR)
                logging.debug("Cleared cache directory")
            os.makedirs(CACHE_DIR, exist_ok=True)
            fav_file = os.path.join(DECKS_DIR, "favorites.txt")
            if os.path.exists(fav_file):
                with open(fav_file, "w") as f:
                    f.write("")
                logging.debug("Cleared favorites")
            card_data = []
            logging.info("Cleared all decks, images, and favorites")
            return jsonify({'status': 'success'})
        else:
            logging.warning(f"Unknown deck action: {action}")
            return jsonify({'status': 'error', 'message': 'Invalid action'}), 400
    except Exception as e:
        logging.error(f"Error in deck action {action}: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/scryfall_search', methods=['POST'])
def scryfall_search():
    """Handle Scryfall search (temporarily disabled)."""
    logging.warning("Scryfall search not yet implemented")
    return jsonify({'status': 'error', 'message': 'Scryfall search not yet implemented'}), 501

@app.route('/logs')
def get_logs():
    """Return log file content."""
    try:
        log_file = os.path.join(LOGS_DIR, "app.log")
        logging.debug(f"Attempting to read log file: {log_file}")
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = f.read()
                logging.info("Served log file content")
                return jsonify({'logs': logs})
        logging.warning(f"Log file not found: {log_file}")
        return jsonify({'logs': ''})
    except Exception as e:
        logging.error(f"Error in get_logs: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

def start_server(browser_instance):
    """Start the Flask server."""
    global card_data
    app.view_functions['index'] = lambda: index(browser_instance)
    app.view_functions['obs_page'] = lambda: obs_page(browser_instance)
    app.view_functions['card_action'] = lambda: card_action(browser_instance)
    app.view_functions['get_cards'] = lambda: get_cards()
    app.view_functions['deck_action'] = lambda: deck_action()
    app.view_functions['scryfall_search'] = lambda: scryfall_search()
    # Load initial card data
    card_data = load_deck_cards()
    from threading import Thread
    server_thread = Thread(target=lambda: app.run(host="localhost", port=8000, debug=True, use_reloader=False))
    server_thread.daemon = True
    server_thread.start()
    logging.info("Flask server started on http://localhost:8000")