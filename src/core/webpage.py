# src/core/webpage.py
# Manages the data model for webpage slots

class WebPage:
    def __init__(self, slot_count=2):
        # Initialize slots with empty strings
        self.slots = [""] * slot_count

    def set_slot(self, slot, image_path):
        # Set the image path for a specific slot (0-based index)
        if 0 <= slot < len(self.slots):
            self.slots[slot] = image_path

    def get_slot(self, slot):
        # Get the image path for a specific slot, return empty string if invalid
        return self.slots[slot] if 0 <= slot < len(self.slots) else ""