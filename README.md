# MTG-OBS
OBS the Gathering - A Magic Card Display

This project was created out of a need to display Magic: The Gathering cards for live events.
I chose to use a local image method in the event that internet connectivity was an issue.

*Inspired by: MagicOBS coded by mathiaspilch & d3kker*

- *This project started out as a fork of MagicOBS but once it became clear that I was rewriting the entire project from scratch I moved it to its own repo.*

**Version**: v0.2.1

## Overview
MTG-OBS is an application that allows users to display Magic: The Gathering cards in OBS using a browser source. The main features of the application include:

- Parsing the default directory of images and displaying them with labels of the image names
- Overlayed on each image are two buttons for slot 1 and slot 2
- The user can click on the corresponding slot button to update the generated index.html 
with the file path of the image.  Additionally, some basic slot logic is applied. Sending to slot 1
will push existing from slot 1 to slot 2.  Sending to slot 2 simply replaces slot 2.
- The images and buttons can be reloaded using the reload button
and filtered using the search field

The add frame button creates a duplicate frame below the default frame which has 
all the same features. However, the new frame will open a dialog box for the user 
to select a new directory of images. This can be used for things like favorite 
or common images that will need to be displayed often to prevent having to 
search for the same card multiple times.

## Technical Details
Each time the app is run, it will check if the `resources/images/clear.png` exists, 
as well as the `style.css` file, and create them if they do not exist. 
The `index.html` file is automatically overwritten each time the application is started
using the `clear.png` file as a placeholder. This ensures that the format of slot 1 
and slot 2 is maintained so that the first card added does not get centered vertically. 
This will also allow for future features where the user can replace a slot with a `clear.png` 
if it is no longer needed. The application also creates the card-images directory when it is run
where the user can place the cards to be loaded in the default frame.

## How to use
1. Download the release MTG-OBS.exe
2. Run the application
3. Place your image files into the generated card-images directory (located in the application root directory)
4. Click the reload button and your images should appear
5. Open OBS
6. Under Sources click `+` and then `Browser`
7. Give the source a name and click ok
8. In the next window click the tick box labeled `Local file` and then Browse.
9. Find your application directory and the index.html will be located in the resources' directory.
10. Set your `Width to 1440` and your `Height to 4022`
11. Tick the Box for Refresh browser when scene becomes active.
`sample properties below`

![Browser-Properties](/README/Browser-Properties.png)

## Future updates
- Improved image quality.
- More advanced search and filter options.
- Additional customization options for the display.
- Options to use decklists like MagicOBS instead of local image files.
- Ability to take any decklist and download local image files from scryfall for local use.