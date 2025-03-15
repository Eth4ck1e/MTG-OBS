# main.py
import os
import atexit
import logging
from datetime import datetime
from src.config.settings import LOGS_DIR
from src.core.webpage import WebPage
from src.gui.window import Window
from src.utils.image import create_clear_png
from src.utils.paths import get_relative_path
from src.web.server import start_server

def cleanup_logs():
    """Rename app.log to a timestamped file on shutdown."""
    logging.shutdown()
    log_file = os.path.join(LOGS_DIR, "app.log")
    if os.path.exists(log_file):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        try:
            os.rename(log_file, os.path.join(LOGS_DIR, f"{timestamp}.log"))
        except PermissionError as e:
            print(f"Warning: Could not rename log file due to {e}")

if __name__ == "__main__":
    atexit.register(cleanup_logs)
    clear_url = create_clear_png()
    browser = WebPage()
    browser.set_slot(0, clear_url)
    browser.set_slot(1, clear_url)
    start_server(browser)
    window = Window(browser=browser)
    window.mainloop()