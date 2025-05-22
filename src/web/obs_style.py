# src/web/obs_style.py
import os
from src.config.settings import OUTPUT_DIR
import logging

def write_obs_style():
    """Generate the CSS file for OBS slot styling in output/obs."""
    obs_dir = os.path.join(OUTPUT_DIR, "obs")
    os.makedirs(obs_dir, exist_ok=True)
    css_path = os.path.join(obs_dir, "style.css")

    css_content = """body {
    margin: 0;
    padding: 0;
    background: transparent;
    overflow: hidden;
}

.container {
    position: relative;
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
}

#slot1 {
    max-width: 100%;
    height: 50vh;
    object-fit: contain;
    margin-bottom: 10px;
}

#slot2 {
    max-width: 100%;
    height: calc(50vh - 10px);
    object-fit: contain;
}
"""
    try:
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css_content)
        logging.info(f"OBS CSS written successfully to {css_path}")
    except Exception as e:
        logging.error(f"Failed to write OBS CSS to {css_path}: {str(e)}", exc_info=True)
        raise

write_obs_style()