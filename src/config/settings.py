# src/config/settings.py
import os
import sys

BASE_DIR = (os.path.dirname(sys.executable) if getattr(sys, 'frozen', False)
            else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
RESOURCE_DIR = os.path.join(BASE_DIR, "resources")  # Static resources (if needed)
CACHE_DIR = os.path.join(BASE_DIR, "cache", "images")
DECKS_DIR = os.path.join(BASE_DIR, "decks")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

SLOT_COUNT = 2
THUMBNAIL_WIDTH = 180
THUMBNAIL_HEIGHT = 250
CLEAR_IMAGE_SIZE = (63, 88)
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700