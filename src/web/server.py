# src/web/server.py
import os
import json
from flask import Flask, render_template_string, send_from_directory, jsonify
from src.config.settings import CACHE_DIR
from src.utils.paths import get_relative_path
from src.utils.image import create_clear_png
import logging

app = Flask(__name__, static_folder=None)


# Serve cache/images only—no output directory
@app.route('/cache/images/<path:filename>')
def cache_images(filename):
    """Serve files from cache/images directory."""
    return send_from_directory(CACHE_DIR, filename)


@app.route('/')
def index(browser):
    """Serve the HTML with slot images and inline CSS/JS."""
    try:
        clear_url = create_clear_png()  # Base64 in-memory clear.png
        slot1 = browser.get_slot(0) or clear_url
        slot2 = browser.get_slot(1) or clear_url

        # Use base64 for clear.png, Flask route for card images
        slot1_url = f"/cache/images/{os.path.basename(slot1)}" if 'cache' in slot1 else slot1
        slot2_url = f"/cache/images/{os.path.basename(slot2)}" if 'cache' in slot2 else slot2

        if 'cache' in slot1 and not os.path.exists(slot1):
            logging.warning(f"Slot 1 file missing: {slot1}")
        if 'cache' in slot2 and not os.path.exists(slot2):
            logging.warning(f"Slot 2 file missing: {slot2}")

        logging.debug(f"Serving index: slot1={slot1_url}, slot2={slot2_url}")

        return render_template_string(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MTG-OBS Overlay</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
        }}
        .container {{
            position: relative;
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            overflow: hidden;
        }}
        #slot1 {{
            max-width: 100%;
            height: calc(50vh - 10px);
            object-fit: contain;
            margin-bottom: 20px;
        }}
        #slot2 {{
            max-width: 100%;
            height: calc(50vh - 10px);
            object-fit: contain;
        }}
    </style>
</head>
<body>
    <div class="container">
        <img id="slot1" src="{slot1_url}">
        <img id="slot2" src="{slot2_url}">
    </div>
    <script>
        function preloadImage(url) {{
            return new Promise((resolve, reject) => {{
                const img = new Image();
                img.onload = () => resolve(img);
                img.onerror = reject;
                img.src = url;
            }});
        }}

        async function updateSlots() {{
            try {{
                const response = await fetch('/slots');
                const data = await response.json();
                const slot1 = document.getElementById('slot1');
                const slot2 = document.getElementById('slot2');
                if (slot1.src !== window.location.origin + data.slot1) {{
                    await preloadImage(data.slot1);
                    slot1.src = data.slot1;
                }}
                if (slot2.src !== window.location.origin + data.slot2) {{
                    await preloadImage(data.slot2);
                    slot2.src = data.slot2;
                }}
            }} catch (error) {{
                console.error('Error updating slots:', error);
            }}
        }}
        setInterval(updateSlots, 1000);
        updateSlots();
    </script>
</body>
</html>
""", browser=browser)
    except Exception as e:
        logging.error(f"Error in index route: {str(e)}", exc_info=True)
        raise


@app.route('/slots')
def get_slots(browser):
    """Return current slot paths as JSON."""
    clear_url = create_clear_png()
    slot1 = browser.get_slot(0) or clear_url
    slot2 = browser.get_slot(1) or clear_url
    slot_data = {
        "slot1": f"/cache/images/{os.path.basename(slot1)}" if 'cache' in slot1 else slot1,
        "slot2": f"/cache/images/{os.path.basename(slot2)}" if 'cache' in slot2 else slot2
    }
    return jsonify(slot_data)


def start_server(browser_instance):
    """Start the Flask server with the given browser instance."""
    app.view_functions['index'] = lambda: index(browser_instance)
    app.view_functions['get_slots'] = lambda: get_slots(browser_instance)

    from threading import Thread
    server_thread = Thread(target=lambda: app.run(host="localhost", port=8000, debug=True, use_reloader=False))
    server_thread.daemon = True
    server_thread.start()
    logging.info("Flask server started on http://localhost:8000")