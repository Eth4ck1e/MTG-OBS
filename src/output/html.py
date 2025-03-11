# src/output/html.py
# Handles HTML and CSS generation

import os
from src.config.settings import RESOURCE_DIR

def create_style_css():
    css_path = os.path.join(RESOURCE_DIR, "style.css")
    if not os.path.isfile(css_path):
        os.makedirs(RESOURCE_DIR, exist_ok=True)
        with open(css_path, "w") as css_file:
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

def write_html(webpage):
    html_path = os.path.join(RESOURCE_DIR, "index.html")
    os.makedirs(RESOURCE_DIR, exist_ok=True)
    html = f"""<!DOCTYPE html>
<html lang="">
<head>
    <link rel="stylesheet" type="text/css" href="style.css">
    <meta http-equiv="refresh" content="0.25">
    <title></title>
</head>
<body>
    <div class="image-container">
        <img src="{webpage.get_slot(0)}" alt="">
        <img src="{webpage.get_slot(1)}" alt="">
    </div>
</body>
</html>"""
    with open(html_path, "w") as html_file:
        html_file.write(html)