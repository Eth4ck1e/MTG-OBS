# src/web/app_html.py
import os
import logging
from src.config.settings import OUTPUT_DIR

def write_app_html():
    """Write the App UI HTML file in output/index.html."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    html_path = os.path.join(OUTPUT_DIR, "index.html")
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MTG-OBS Reborn</title>
    <style>
        body {
            margin: 0;
            padding: 10px;
            background: #333333;
            color: #e0e0e0;
            font-family: Arial, sans-serif;
        }
        .tabs {
            display: flex;
            margin-bottom: 10px;
        }
        .tab {
            padding: 10px;
            background: #4a4a4a;
            cursor: pointer;
            margin-right: 5px;
        }
        .tab.active {
            background: #777777;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .controls {
            margin-bottom: 10px;
        }
        .controls button {
            background: #555555;
            color: #000000;
            border: none;
            padding: 5px 10px;
            margin-right: 5px;
            cursor: pointer;
        }
        .controls button:hover {
            background: #777777;
        }
        .controls input {
            background: #444444;
            color: #e0e0e0;
            border: none;
            padding: 5px;
            margin-right: 5px;
        }
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
        }
        .card {
            position: relative;
            text-align: center;
            background: #444444;
            padding: 5px;
            border-radius: 5px;
        }
        .card img {
            width: 100%;
            height: auto;
            object-fit: contain;
        }
        .card-name {
            font-size: 12px;
            margin: 5px 0;
        }
        .card-buttons {
            display: flex;
            justify-content: space-between;
        }
        .card-buttons button {
            background: #555555;
            color: #000000;
            border: none;
            padding: 5px;
            cursor: pointer;
            font-size: 10px;
        }
        .card-buttons button:hover {
            background: #777777;
        }
        .context-menu {
            position: absolute;
            background: #4a4a4a;
            color: #e0e0e0;
            border: 1px solid #555555;
            z-index: 100;
        }
        .context-menu div {
            padding: 5px;
            cursor: pointer;
        }
        .context-menu div:hover {
            background: #777777;
        }
        #logContent {
            background: #444444;
            padding: 10px;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/fuse.js@7.0.0"></script>
</head>
<body>
    <div class="tabs">
        <div class="tab active" onclick="showTab('decks')">Decks</div>
        <div class="tab" onclick="showTab('logs')">Logs</div>
    </div>
    <div id="decks" class="tab-content active">
        <div class="controls">
            <button onclick="deckAction('reload')">Reload</button>
            <button onclick="deckAction('clear')">Clear All</button>
            <input type="file" id="deckFile" accept=".txt" style="display: none;">
            <button onclick="document.getElementById('deckFile').click()">Add Deck</button>
            <label>Search:</label>
            <input type="text" id="searchField" oninput="filterCards(this.value)">
        </div>
        <h3>Favorites</h3>
        <div class="card-grid" id="favoritesGrid"></div>
        <h3>Cards</h3>
        <div class="card-grid" id="cardGrid"></div>
    </div>
    <div id="logs" class="tab-content">
        <div id="logContent"></div>
    </div>
    <script src="/app.js"></script>
</body>
</html>
"""
    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logging.info(f"App HTML written successfully to {html_path}")
    except Exception as e:
        logging.error(f"Failed to write App HTML to {html_path}: {str(e)}", exc_info=True)
        raise

write_app_html()