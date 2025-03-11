# main.py
import os
import atexit
import logging
from datetime import datetime
from src.config.settings import RESOURCE_DIR, LOGS_DIR
from src.core.webpage import WebPage
from src.gui.window import Window
from src.output.html import write_html, create_style_css
from src.utils.image import create_clear_png
from src.utils.paths import get_relative_path

def cleanup_logs():
    """Rename app.log to a timestamped file on shutdown after closing logging handlers."""
    logging.shutdown()  # Close all logging handlers to release file locks
    log_file = os.path.join(LOGS_DIR, "app.log")
    if os.path.exists(log_file):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        try:
            os.rename(log_file, os.path.join(LOGS_DIR, f"{timestamp}.log"))
        except PermissionError as e:
            print(f"Warning: Could not rename log file due to {e}. It may still be in use.")

if __name__ == "__main__":
    atexit.register(cleanup_logs)  # Register cleanup function for shutdown
    create_clear_png()
    browser = WebPage()
    create_style_css()
    clear_path = get_relative_path(os.path.join(RESOURCE_DIR, "images"), "clear.png")
    browser.set_slot(0, clear_path)
    browser.set_slot(1, clear_path)
    write_html(browser)
    window = Window(browser=browser)
    window.mainloop()