# src/web/obs_html.py
import os
from src.config.settings import OUTPUT_DIR, CACHE_DIR
from src.utils.image import create_clear_png
import logging

def write_obs_html(browser):
    """Write the OBS HTML file with slot images in output/obs."""
    obs_dir = os.path.join(OUTPUT_DIR, "obs")
    os.makedirs(obs_dir, exist_ok=True)
    html_path = os.path.join(obs_dir, "index.html")
    css_path = os.path.join(obs_dir, "style.css")

    clear_url = create_clear_png()
    slot1_path = browser.get_slot(0) if browser.get_slot(0) else clear_url
    slot2_path = browser.get_slot(1) if browser.get_slot(1) else clear_url

    # Use /cache/images/ for cached images, base64 for clear.png
    slot1_url = f"/cache/images/{os.path.basename(slot1_path)}" if 'cache' in slot1_path.lower() else slot1_path
    slot2_url = f"/cache/images/{os.path.basename(slot2_path)}" if 'cache' in slot2_path.lower() else slot2_path

    if 'cache' in slot1_path.lower() and not os.path.exists(slot1_path):
        logging.warning(f"Slot 1 path does not exist: {slot1_path}")
    if 'cache' in slot2_path.lower() and not os.path.exists(slot2_path):
        logging.warning(f"Slot 2 path does not exist: {slot2_path}")
    if not os.path.exists(css_path):
        logging.warning(f"OBS CSS path does not exist: {css_path}")

    logging.debug(f"Writing OBS HTML: slot1={slot1_url}, slot2={slot2_url}, css={css_path}")

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MTG-OBS Reborn</title>
    <link rel="stylesheet" href="/obs/style.css">
</head>
<body>
    <div class="container">
        <img id="slot1" src="{slot1_url}" alt="Slot 1">
        <img id="slot2" src="{slot2_url}" alt="Slot 2">
    </div>
    <script>
        let lastSlots = {{ slot1: "{slot1_url}", slot2: "{slot2_url}" }};
        async function checkSlots() {{
            try {{
                const response = await fetch('/slots');
                const slots = await response.json();
                if (slots.slot1 !== lastSlots.slot1 || slots.slot2 !== lastSlots.slot2) {{
                    window.location.reload();
                }}
                lastSlots = slots;
            }} catch (error) {{
                console.error('Error checking slots:', error);
            }}
        }}
        setInterval(checkSlots, 1000); // Poll every 1 second
    </script>
</body>
</html>
"""
    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logging.info(f"OBS HTML written successfully to {html_path}")
    except Exception as e:
        logging.error(f"Failed to write OBS HTML to {html_path}: {str(e)}", exc_info=True)
        raise