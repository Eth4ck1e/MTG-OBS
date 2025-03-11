# src/utils/paths.py
# Path-related utilities

import os

def get_relative_path(image_directory, filename):
    return os.path.relpath(os.path.join(image_directory, filename))