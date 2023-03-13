MTG-OBS - OBS the Gathering - A Magic Card Display
MTG-OBS is a Python application that enables users to display Magic: The Gathering cards in OBS using a browser source.

Features
Parses the default directory of images and displays them with labels of the image names.
Overlayed on each image are two buttons for slot 1 and slot 2. The user can click on the corresponding slot button to update the generated index.html with the file path of the image.
The images and buttons can be reloaded using the reload button and filtered using the search field.
The add frame button creates a duplicate frame below the default frame which has all the same features.
The new frame will open a dialog box for the user to select a new directory of images.
The app checks if the resources/images/clear.png and style.css files exist when the app is run. If not, it creates them.
The index.html file is automatically overwritten each time the application is started using the clear.png as a placeholder.
This ensures the format of slot 1 and slot 2 is maintained so that the first card added does not get centered vertically.
This will also allow for future features where the user can replace a slot with a clear.png if it is no longer needed.
Version
Version: v0.2.1
How to use
Download the MTG-OBS project files.
Install the required packages using pip install -r requirements.txt.
Run python main.py to start the application.
Click on the slot buttons to add Magic: The Gathering cards to the display.
Future updates
Improved image quality.
More advanced search and filter options.
Additional customization options for the display.
