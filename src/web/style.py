# src/web/style.py
import os
from src.config.settings import OUTPUT_DIR
import logging


def write_style():
    """Generate the CSS file for slot styling."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    css_path = os.path.join(OUTPUT_DIR, "style.css")

    css_content = """body {
    margin: 0;
    padding: 0;
    background: transparent;
}

.container {
    position: relative;
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;  /* Start from top */
    overflow: hidden;
}

#slot1 {
    max-width: 100%;
    height: 50vh;  /* Half viewport height */
    object-fit: contain;
    margin-bottom: 10px;  /* Buffer between slots only */
}

#slot2 {
    max-width: 100%;
    height: calc(50vh - 10px);  /* Remaining height minus buffer */
    object-fit: contain;
}
"""
    try:
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css_content)
        logging.info(f"CSS written successfully to {css_path}")
    except Exception as e:
        logging.error(f"Failed to write CSS: {str(e)}", exc_info=True)


write_style()