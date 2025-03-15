# src/web/html.py
import os
from src.config.settings import OUTPUT_DIR, CACHE_DIR
import logging


def write_html(browser):
    """Write the HTML file with slot images."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    html_path = os.path.join(OUTPUT_DIR, "index.html")
    css_path = os.path.join(OUTPUT_DIR, "style.css")
    clear_path = os.path.join(OUTPUT_DIR, "images", "clear.png")

    slot1_path = browser.get_slot(0) if browser.get_slot(0) else clear_path
    slot2_path = browser.get_slot(1) if browser.get_slot(1) else clear_path

    if not os.path.exists(slot1_path):
        logging.warning(f"Slot 1 path does not exist: {slot1_path}")
    if not os.path.exists(slot2_path):
        logging.warning(f"Slot 2 path does not exist: {slot2_path}")
    if not os.path.exists(css_path):
        logging.warning(f"CSS path does not exist: {css_path}")

    logging.debug(f"Writing HTML: slot1={slot1_path}, slot2={slot2_path}, css={css_path}")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MTG-OBS Overlay</title>
    <link rel="stylesheet" href="{os.path.relpath(css_path, OUTPUT_DIR).replace(os.sep, '/')}">
</head>
<body>
    <div class="container">
        <img id="slot1" src="{os.path.relpath(slot1_path, OUTPUT_DIR).replace(os.sep, '/')}">
        <img id="slot2" src="{os.path.relpath(slot2_path, OUTPUT_DIR).replace(os.sep, '/')}">
    </div>
</body>
</html>
"""
    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logging.info(f"HTML written successfully to {html_path}")
    except Exception as e:
        logging.error(f"Failed to write HTML: {str(e)}", exc_info=True)