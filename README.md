# MTG-OBS Reborn
OBS the Gathering - A Magic Card Display

This project was born from the need to showcase Magic: The Gathering cards during live events, using local images to ensure reliability even without internet access.

*Inspired by: MagicOBS by mathiaspilch & d3kker*
*Originally a fork of MagicOBS, this project evolved into a full rewrite and now stands on its own.*

**Version**: v1.7.0

## Overview
MTG-OBS lets you display Magic: The Gathering cards in OBS via a browser source. Key features include:

- Parses Archidekt-exported deck lists into a sleek, modern interface.
- Cards feature overlay buttons: "Slot 1", "Slot 2", and "Fav" for quick slot updates or favoriting.
  - "Slot 1" pushes existing Slot 1 to Slot 2; "Slot 2" replaces directly; "Fav" adds to a dedicated frame.
- "Reload" refreshes images, "Clear All" resets decks, and "Add Deck" imports new deck files.
- "Clear Fav" also clears the favorites frame of all cards.
- Dynamic search filters cards in real-time.
- Updated theme with customizable colors and rounded buttons for a polished look.
- The application requires an internet connection to download and cache the card images for all the decks.  It also requires an internet connection to use the scryfall search feature.

## Technical Details
- **Startup**: Starts a local web server at http://localhost:8000/ and places two clear.png card images as placeholders on the page.
- **Directories**: Batch downloads all decklist `card-images` from Scryfall for default card storage and `cache` for card images.
- **UI**: 
  - Primary Deck Tab for selecting cards to appear in OBS Browser source.
    - Right-clicking on a card in the deck tab will open a dialog to replace a card. Once selected the user will be automatically taken to the scryfall search tab (card will be searched for automatically) to select a card to replace the original.
  - Log tab for review.  
  - Scryfall Search tab for manual card searching and adding to the decks frame.
- **Adding Decks**: 
  - If a decklist is placed in the decks directory (If one does not exist it will be created in the root of the application directory) it will be parsed automatically.
  - You can also click the "Add Deck" button to open a file browser window and select a deck list to be imported.  It will be copied to the decks directory parsed and automatically downloaded from Scryfall.

## How to Use
1. Download `MTG-OBS.exe` from the latest release.
2. Run the app—it creates necessary directories (`decks`, `cache`, `logs`) aswell as the setup.yaml for future configuration updates.
3. Add your deck lists to the decks directory or use the "Add Deck" button to add one at a time.
4. Use the Search field to filter cards and select the slot you wish the card to appear.
5. Setup OBS:
   - Add a Browser source (`+` > "Browser").
   - Name it, click "OK".
   - paste "http://localhost:8000/" into the URL field.
   - Set `Width` to 1440, `Height` to 4022.
   - Enable "Refresh browser when scene becomes active".
   - **(IMPORTANT)** Set the `Page permissions to Basic access to OBS (Save replay buffer, etc.)`
   - See screenshot of Browser properties below:

![Browser-Properties](/README/Browser-Properties.png)

## Future Updates
- Enhanced logging for better debugging and user feedback.