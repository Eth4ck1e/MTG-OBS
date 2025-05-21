# src/utils/image.py
import os
import requests
import time
import logging
from datetime import datetime
from src.config.settings import CACHE_DIR, CLEAR_IMAGE_SIZE, LOGS_DIR
from PIL import Image, ImageTk
import io
import base64

# Logging setup (LOGS_DIR is already created by settings.py)
log_file = os.path.join(LOGS_DIR, "app.log")
if os.path.exists(log_file):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.rename(log_file, os.path.join(LOGS_DIR, f"{timestamp}.log"))
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

class CustomImage:
    def __init__(self, directory, name):
        self.directory = directory
        self.name = name
        self.thumbnail = None

    def load_thumbnail(self, button_width, button_height):
        image_path = os.path.join(self.directory, self.name)
        image = Image.open(image_path)
        image = image.resize((button_width, button_height), resample=Image.LANCZOS)
        self.thumbnail = ImageTk.PhotoImage(image)

def create_clear_png():
    """Create clear.png in memory as a base64 string."""
    width, height = CLEAR_IMAGE_SIZE
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    base64_str = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
    logging.info("Clear.png created in memory as base64 string.")
    buffer.close()
    return base64_str

def download_scryfall_images(cards):
    """Download images for a list of cards in bulk from Scryfall."""
    # CACHE_DIR is already created by settings.py
    base_url = "https://api.scryfall.com/cards/collection"
    headers = {"Content-Type": "application/json"}
    identifiers = [
        {"set": card["set_code"], "collector_number": card["collector_number"]}
        for card in cards
    ]
    all_image_paths = []

    logging.debug(f"Starting download for {len(identifiers)} cards")
    for i in range(0, len(identifiers), 75):
        batch = identifiers[i:i + 75]
        batch_cards = cards[i:i + 75]
        payload = {"identifiers": batch}
        batch_paths = []
        try:
            response = requests.post(base_url, json=payload, headers=headers)
            response.raise_for_status()
            card_data = response.json()["data"]
            for card, orig_card in zip(card_data, batch_cards):
                safe_name = f"{card['name'].replace(' ', '_').replace('/', '_')}_{card['set']}_{card['collector_number']}.png"
                file_path = os.path.join(CACHE_DIR, safe_name)
                image_paths = []

                if "card_faces" in card and card["layout"] in ["modal_dfc", "transform"]:
                    for face in card["card_faces"]:
                        face_name = face["name"].replace(" ", "_").replace("/", "_")
                        face_file = f"{face_name}_{card['set']}_{card['collector_number']}.png"
                        face_path = os.path.join(CACHE_DIR, face_file)
                        if not os.path.isfile(face_path):
                            image_url = face["image_uris"]["png"] if not orig_card["is_foil"] else face.get("image_uris", {}).get("png")
                            with requests.get(image_url) as img_response:
                                img_response.raise_for_status()
                                with open(face_path, "wb") as f:
                                    f.write(img_response.content)
                        image_paths.append(face_path)
                else:
                    if not os.path.isfile(file_path):
                        image_url = card["image_uris"]["png"] if not orig_card["is_foil"] else card.get("image_uris", {}).get("png")
                        with requests.get(image_url) as img_response:
                            img_response.raise_for_status()
                            with open(file_path, "wb") as f:
                                f.write(img_response.content)
                    image_paths.append(file_path)

                batch_paths.extend(image_paths)
                logging.debug(f"Downloaded images for {card['name']} ({card['set']} #{card['collector_number']})")
            all_image_paths.extend(batch_paths)
            time.sleep(0.1)
        except Exception as e:
            logging.error(f"Failed to fetch Scryfall batch: {str(e)}", exc_info=True)
            for card in batch_cards:
                if not any(basic in card["card_name"] for basic in ["Island", "Mountain", "Swamp", "Forest", "Plains"]):
                    logging.warning(f"Failed to download {card['card_name']} ({card['set_code']} #{card['collector_number']})")
    logging.debug(f"Completed download: {len(all_image_paths)} paths")
    return all_image_paths

def download_scryfall_image(card_name, set_code, collector_number, is_foil=False, cache_dir=CACHE_DIR):
    """Legacy single-card fetch (kept for compatibility)."""
    return download_scryfall_images(
        [{"card_name": card_name, "set_code": set_code, "collector_number": collector_number, "is_foil": is_foil}])