# src/utils/image.py
import os
import requests
import time
import logging
from datetime import datetime
from src.config.settings import RESOURCE_DIR, CACHE_DIR, CLEAR_IMAGE_SIZE, LOGS_DIR
from PIL import Image, ImageTk

# Configure logging with cleanup
os.makedirs(LOGS_DIR, exist_ok=True)
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
    width, height = CLEAR_IMAGE_SIZE
    directory = os.path.join(RESOURCE_DIR, "images")
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, "clear.png")
    if os.path.isfile(file_path):
        print("File already exists, skipping creation.")
        return
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    image.save(file_path, "PNG")
    print("File created successfully.")


def download_scryfall_image(card_name, set_code, collector_number, is_foil=False, cache_dir=CACHE_DIR):
    os.makedirs(cache_dir, exist_ok=True)
    safe_name = f"{card_name.replace(' ', '_').replace('/', '_')}_{set_code}_{collector_number}.png"
    file_path = os.path.join(cache_dir, safe_name)

    if os.path.isfile(file_path):
        return [file_path]

    url = f"https://api.scryfall.com/cards/{set_code}/{collector_number}"
    try:
        response = requests.get(url)
        time.sleep(0.1)  # Rate limit
        if response.status_code != 200:
            logging.error(
                f"Scryfall query failed for {card_name} ({set_code} #{collector_number}): HTTP {response.status_code}")
            return []

        card_data = response.json()
        if "Land" in card_data.get("type_line", "") and "Basic" in card_data.get("type_line", ""):
            return []  # Skip basic lands

        image_paths = []
        if "card_faces" in card_data and card_data["layout"] in ["modal_dfc", "transform"]:
            for face in card_data["card_faces"]:
                face_name = face["name"].replace(" ", "_").replace("/", "_")
                face_file = f"{face_name}_{set_code}_{collector_number}.png"
                face_path = os.path.join(cache_dir, face_file)
                if not os.path.isfile(face_path):
                    image_url = face["image_uris"]["png"] if not is_foil else face.get("image_uris", {}).get("png")
                    image_response = requests.get(image_url)
                    with open(face_path, "wb") as f:
                        f.write(image_response.content)
                image_paths.append(face_path)
        else:
            if not os.path.isfile(file_path):
                image_url = card_data["image_uris"]["png"] if not is_foil else card_data.get("image_uris", {}).get(
                    "png")
                image_response = requests.get(image_url)
                with open(file_path, "wb") as f:
                    f.write(image_response.content)
            image_paths.append(file_path)
        return image_paths
    except Exception as e:
        logging.error(f"Error downloading {card_name} ({set_code} #{collector_number}): {str(e)}")
        return []