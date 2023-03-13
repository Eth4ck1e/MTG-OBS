import os


class WebPage:
    def __init__(self, image_paths=None, slots=None):
        if image_paths is None:
            image_paths = ["", ""]
        self.image_path_1 = image_paths[0]
        self.image_path_2 = image_paths[1]
        self.slots = slots


def create_style_css():
    # Check if the style.css file exists and create it if not
    if not os.path.isfile("resources/style.css"):
        with open("resources/style.css", "w") as css_file:
            css_file.write(".image-container {\n"
                           "  width: 1440px;\n"
                           "  height: 4022px;\n"
                           "  background-color: transparent;\n"
                           "  display: flex;\n"
                           "  flex-direction: column;\n"
                           "  justify-content: center;\n"
                           "  align-items: center;\n"
                           "}\n\n"
                           "img {\n"
                           "  width: 100%;\n"
                           "  height: auto;\n"
                           "  padding: 10px 0;\n"
                           "}\n")


def write_html_file(webpage_object, image_path, slot):
    """
    Write an HTML file linking to the CSS file and displaying the specified image in the appropriate slot.

    Args:
        image_path (str): The path to the image file.
        slot (int): The slot number (1 or 2) to display the image in.
        :param webpage_object:
        :param slot:
        :param image_path:
    """

    # Determine the image file paths based on the provided image_path and slot
    if slot == 1:
        webpage_object.image_path_2, webpage_object.image_path_1 = webpage_object.image_path_1, image_path
    elif slot == 2:
        webpage_object.image_path_2 = image_path

    # Generate the HTML code
    html = f"""<!DOCTYPE html>
<html lang="">
<head>
\t<link rel="stylesheet" type="text/css" href="style.css">
\t<meta http-equiv="refresh" content="0.25">
\t<title></title>
</head>
<body>
\t<div class="image-container">
\t\t<img src="{webpage_object.image_path_1}" alt="">
\t\t<img src="{webpage_object.image_path_2}" alt="">
\t</div>
</body>
</html>"""

    # Write the HTML code to a file
    with open("resources/index.html", "w") as html_file:
        html_file.write(html)
