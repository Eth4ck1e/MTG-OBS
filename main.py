# main.py
import os
import atexit
import logging
import webbrowser
import time
from datetime import datetime
from src.config.settings import LOGS_DIR
from src.core.webpage import WebPage
from src.utils.image import create_clear_png
from src.web.app_server import start_server
from src.web.obs_style import write_obs_style
from src.web.obs_html import write_obs_html
from src.web.app_html import write_app_html
from src.web.app_js import write_app_js

def cleanup_logs():
    """Rename app.log to a timestamped file on shutdown."""
    logging.shutdown()
    log_file = os.path.join(LOGS_DIR, "app.log")
    if os.path.exists(log_file):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        target_path = os.path.join(LOGS_DIR, f"{timestamp}.log")
        counter = 1
        while os.path.exists(target_path):
            target_path = os.path.join(LOGS_DIR, f"{timestamp}_{counter}.log")
            counter += 1
        try:
            os.rename(log_file, target_path)
        except PermissionError as e:
            print(f"Warning: Could not rename log file due to {e}")

if __name__ == "__main__":
    atexit.register(cleanup_logs)
    logging.info("Starting app initialization")
    try:
        write_obs_style()
        write_app_html()
        write_app_js()
        clear_url = create_clear_png()
        browser = WebPage()
        browser.set_slot(0, clear_url)
        browser.set_slot(1, clear_url)
        write_obs_html(browser)
        start_server(browser)
        logging.info("Opening browser to http://localhost:8000/")
        webbrowser.open("http://localhost:8000/")
        # Keep main thread alive
        logging.info("App running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)  # Prevent CPU overload
    except KeyboardInterrupt:
        logging.info("App shutdown requested")
    except Exception as e:
        logging.error(f"Error during app initialization: {str(e)}", exc_info=True)
        raise