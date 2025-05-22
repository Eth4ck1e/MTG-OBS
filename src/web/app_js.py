# src/web/app_js.py
import os
import logging
from src.config.settings import OUTPUT_DIR

def write_app_js():
    """Write the App UI JavaScript file in output."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    js_path = os.path.join(OUTPUT_DIR, "app.js")
    js_content = """let allCards = [];
let fuse;

async function loadCards() {
    console.log("Loading cards...");
    try {
        const response = await fetch('/cards');
        allCards = await response.json();
        console.log(`Fetched ${allCards.length} cards`);
        if (allCards.length === 0) {
            document.getElementById('cardGrid').innerHTML = '<p>No cards found. Add images to cache directory.</p>';
            console.warn("No cards returned from /cards");
        } else {
            fuse = new Fuse(allCards, {
                keys: ['name'],
                threshold: 0.4,
                includeScore: true
            });
            renderCards(allCards);
        }
        loadFavorites();
    } catch (error) {
        console.error("Error loading cards:", error);
        document.getElementById('cardGrid').innerHTML = '<p>Error loading cards. Check console for details.</p>';
    }
}

async function loadFavorites() {
    console.log("Loading favorites...");
    try {
        const response = await fetch('/favorites');
        const favorites = await response.json();
        console.log(`Fetched ${favorites.length} favorites`);
        const grid = document.getElementById('favoritesGrid');
        if (favorites.length === 0) {
            grid.innerHTML = '<p>No favorites found.</p>';
        } else {
            favorites.forEach((card, index) => {
                const cardDiv = document.createElement('div');
                cardDiv.className = 'card';
                cardDiv.innerHTML = `
                    <img src="/cache/images/${card.filename}" alt="${card.name}">
                    <div class="card-name">${card.name}</div>
                    <div class="card-buttons">
                        <button onclick="action('slot1', ${index}, 'favorites')">Slot 1</button>
                        <button onclick="action('slot2', ${index}, 'favorites')">Slot 2</button>
                    </div>
                `;
                grid.appendChild(cardDiv);
            });
        }
    } catch (error) {
        console.error("Error loading favorites:", error);
        document.getElementById('favoritesGrid').innerHTML = '<p>Error loading favorites.</p>';
    }
}

function renderCards(cards) {
    console.log(`Rendering ${cards.length} cards`);
    const grid = document.getElementById('cardGrid');
    grid.innerHTML = '';
    cards.forEach((card, index) => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'card';
        cardDiv.innerHTML = `
            <img src="/cache/images/${card.filename}" alt="${card.name}">
            <div class="card-name">${card.name}</div>
            <div class="card-buttons">
                <button onclick="action('fav', ${index})">Fav</button>
                <button onclick="action('slot1', ${index})">Slot 1</button>
                <button onclick="action('slot2', ${index})">Slot 2</button>
            </div>
        `;
        cardDiv.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            showContextMenu(e, index);
        });
        grid.appendChild(cardDiv);
    });
}

function showContextMenu(event, index) {
    console.log(`Showing context menu for card index ${index}`);
    const existingMenu = document.querySelector('.context-menu');
    if (existingMenu) existingMenu.remove();
    const menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.style.left = `${event.pageX}px`;
    menu.style.top = `${event.pageY}px`;
    menu.innerHTML = `<div onclick="action('replace', ${index})">Replace Card</div>`;
    document.body.appendChild(menu);
    document.addEventListener('click', () => menu.remove(), { once: true });
}

async function action(type, index, source = 'cards') {
    console.log(`Performing action: type=${type}, index=${index}, source=${source}`);
    try {
        const response = await fetch('/card_action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, index, source })
        });
        const data = await response.json();
        if (response.ok && (type === 'fav' || type === 'replace')) {
            loadCards();
            loadFavorites();
        } else if (!response.ok) {
            console.error(`Action failed: ${data.message}`);
            alert(data.message);
        }
    } catch (error) {
        console.error(`Error in action ${type}:`, error);
        alert("Action failed. Check console for details.");
    }
}

async function deckAction(action) {
    console.log(`Performing deck action: ${action}`);
    try {
        if (action === 'add_deck') {
            const fileInput = document.getElementById('deckFile');
            if (!fileInput.files[0]) {
                console.warn("No deck file selected");
                alert("Please select a deck file.");
                return;
            }
            const formData = new FormData();
            formData.append('deck_file', fileInput.files[0]);
            console.log("Uploading deck file:", fileInput.files[0].name);
            const response = await fetch('/deck_action', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (response.ok) {
                console.log("Deck added successfully");
                fileInput.value = '';
                loadCards();
                loadFavorites();
            } else {
                console.error(`Deck action failed: ${data.message}`);
                alert(data.message);
            }
        } else {
            const response = await fetch('/deck_action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action })
            });
            const data = await response.json();
            if (response.ok) {
                console.log(`Deck action ${action} successful`);
                loadCards();
                loadFavorites();
            } else {
                console.error(`Deck action failed: ${data.message}`);
                alert(data.message);
            }
        }
    } catch (error) {
        console.error(`Error in deck action ${action}:`, error);
        alert("Deck action failed. Check console for details.");
    }
}

function filterCards(search) {
    console.log(`Filtering cards with search: ${search}`);
    if (!search) {
        renderCards(allCards);
        return;
    }
    const results = fuse.search(search).map(result => result.item);
    renderCards(results.length ? results : []);
}

async function loadLogs() {
    console.log("Loading logs...");
    try {
        const response = await fetch('/logs');
        const data = await response.json();
        console.log("Logs fetched:", data.logs ? `${data.logs.length} chars` : "empty");
        document.getElementById('logContent').textContent = data.logs;
    } catch (error) {
        console.error("Error loading logs:", error);
        document.getElementById('logContent').innerHTML = '<p>Error loading logs.</p>';
    }
}

function showTab(tabId) {
    console.log(`Switching to tab: ${tabId}`);
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    document.querySelector(`.tab[onclick="showTab('${tabId}')"]`).classList.add('active');
    if (tabId === 'logs') loadLogs();
}

console.log("Initializing app...");
loadCards();
"""
    try:
        with open(js_path, "w", encoding="utf-8") as f:
            f.write(js_content)
        logging.info(f"App JS written successfully to {js_path}")
    except Exception as e:
        logging.error(f"Failed to write App JS to {js_path}: {str(e)}", exc_info=True)
        raise

write_app_js()