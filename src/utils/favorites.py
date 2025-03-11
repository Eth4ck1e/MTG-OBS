# src/utils/favorites.py
import os
from src.config.settings import DECKS_DIR, CACHE_DIR
from src.utils.image import CustomImage

def save_favorite(filename):
    """Save a card filename to favorites.txt."""
    with open(os.path.join(DECKS_DIR, "favorites.txt"), "a") as f:
        f.write(f"{filename}\n")

def load_favorites(button_width, button_height):
    """Load favorites from favorites.txt and return as CustomImage list."""
    images = []
    fav_file = os.path.join(DECKS_DIR, "favorites.txt")
    if os.path.exists(fav_file):
        with open(fav_file, "r") as f:
            for line in f:
                filename = line.strip()
                if os.path.exists(os.path.join(CACHE_DIR, filename)):
                    image = CustomImage(CACHE_DIR, filename)
                    image.load_thumbnail(button_width, button_height)
                    images.append(image)
    return images