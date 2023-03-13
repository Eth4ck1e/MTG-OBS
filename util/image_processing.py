import os
import tkinter

from PIL import Image, ImageTk


def resize_image(image_path, button_width, button_height):
    photo_image = tkinter.PhotoImage(file=image_path)
    return photo_image.subsample(int(photo_image.width() / button_width), int(photo_image.height() / button_height))


def get_relative_path(image_directory, filename):
    """
    Returns the relative path of the image file given its directory and filename.

    Args:
        image_directory (str): The path to the image directory.
        filename (str): The name of the image file.

    Returns:
        str: The relative path of the image file.
    """
    return os.path.relpath(os.path.join(image_directory, filename))


class CustomImage:
    def __init__(self, directory, name):
        self.directory = directory
        self.name = name
        self.thumbnail = None

    def load_thumbnail(self, button_width, button_height):
        image_path = os.path.join(self.directory, self.name)

        # Open the image file
        image = Image.open(image_path)

        # Resize the image
        image = image.resize((button_width, button_height), resample=Image.LANCZOS)

        # Convert the image to PhotoImage format
        self.thumbnail = ImageTk.PhotoImage(image)


def create_clear_png():
    # Set the size of the image
    width, height = 63, 88

    # Check if the images directory exists, create it if it doesn't
    directory = "resources/images"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Check if the file already exists
    file_path = os.path.join(directory, "clear.png")
    if os.path.isfile(file_path):
        print("File already exists, skipping creation.")
        return

    # Create the image and save it
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    image.save(file_path, "PNG")
    print("File created successfully.")
