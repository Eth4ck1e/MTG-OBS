# src/config/settings.py
import os
import sys

# Determine the root directory based on executable or script location
if hasattr(sys, 'frozen'):  # Running as PyInstaller .exe
    ROOT_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:  # Running as script
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Filepaths
DECKS_DIR = os.path.join(ROOT_DIR, "decks")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
CACHE_DIR = os.path.join(ROOT_DIR, "cache")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")

# Create directories if they don't exist
for directory in [DECKS_DIR, LOGS_DIR, CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)

# Images
THUMBNAIL_WIDTH = 100  # Legacy, kept for compatibility
THUMBNAIL_HEIGHT = 140  # Legacy, kept for compatibility

# Frame Thumbnails
SCALE = 2
CARD_WIDTH = THUMBNAIL_WIDTH * SCALE  # New card display size
CARD_HEIGHT = THUMBNAIL_HEIGHT * SCALE  # New card display size

CLEAR_IMAGE_SIZE = (672, 936)

# Window
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 800
WINDOW_TITLE = "MTG-OBS Reborn"

# UI Colors
PRIMARY_BG_COLOR = "#333333"    # Charcoal background
SECONDARY_BG_COLOR = "#4a4a4a"  # Controls/settings bg
WIDGET_BG_COLOR = "#555555"     # Buttons, dropdowns
WIDGET_ACTIVE_COLOR = "#777777" # Hover/selected
TEXT_COLOR = "#e0e0e0"          # Light gray
CONTROL_TEXT_COLOR = "#000000"  # Black
FIELD_BG_COLOR = "#444444"      # Entry/dropdown field

# Fonts
DEFAULT_FONT = ("Arial", 12)
BOLD_FONT = ("Arial", 12, "bold")

# Button Widths
SLOT_BUTTON_WIDTH = 7
FAV_BUTTON_WIDTH = 3