import os
import tkinter as tk
from tkinter import messagebox, ttk

from util.html_source import write_html_file
from util.image_processing import CustomImage, get_relative_path


def open_dialog_box():
    print("open_dialog_box function needs to be replaced.  Instead of opening a dialog box I want there to be two "
          "buttons on each image.  1 button to send to slot 1 and another button to send to slot 2")


class CustomFrame(tk.Frame):
    def __init__(self, parent, browser, button_width=180, button_height=250, image_directory=None, padding=10):
        tk.Frame.__init__(self, parent, height=100)

        self.frame_buttons = tk.Frame(self)
        self.search_field = tk.Entry(self.frame_buttons, width=30)
        self.image_frame = tk.Frame(self)
        self.list_of_buttons = []
        self.button_width = int(button_width)
        self.button_height = int(button_height)
        self.image_directory = image_directory
        self.images = []
        self.padding = padding

        self.create_widgets(browser)

    def create_widgets(self, browser):

        # Create the interface button frame and add it to the top
        self.frame_buttons.pack(side=tk.TOP, fill=tk.X)

        # Create the images frame and add it to the bottom
        self.image_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create the reload button and add it to the interface button frame
        reload_button = tk.Button(self.frame_buttons, text="Reload",
                                  command=lambda: self.reload_images(browser, self.image_directory), width=20)
        reload_button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding, anchor=tk.NW, expand=False)

        # Create a label for the search field
        search_label = tk.Label(self.frame_buttons, text="Search:")
        search_label.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)

        # Create the search field and add it to the interface button frame
        self.search_field.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
        self.search_field.bind("<KeyRelease>", self.filter_cards)

        self.load_images_with_progress(browser, self.image_directory)

    # def update_grid_size(self, event, frame):
    #     # Delay the call to calculate_grid_size until the window has been fully initialized
    #     rows, cols = self.calculate_grid_size()
    #     self.create_grid_of_buttons(rows, cols, frame)

    def calculate_grid_size(self):
        total_width = self.winfo_width() - self.padding
        cols = max(1, int(total_width / (self.button_width + self.padding)))
        rows = max(1, int(len(self.images) / cols))
        if len(self.images) % cols != 0:
            rows += 1
        return rows, cols

    def create_grid_of_buttons(self, rows, cols, browser):
        # Clear the list of buttons
        self.list_of_buttons = []

        # Clear the image frame
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        index = 0
        for row in range(rows):
            for col in range(cols):
                if index >= len(self.images):
                    break

                # Get filename of the image
                filename = self.images[index].name

                # Create label with image thumbnail
                label = tk.Label(self.image_frame, image=self.images[index].thumbnail,
                                 width=self.button_width, height=self.button_height)

                # Add label as a separate widget on top of the button
                label_name = tk.Label(label, text=filename, fg="white", font=("Helvetica", 10), bg="#333333")
                label_name.place(relx=0.5, rely=0.5, anchor="center")

                # Add SLOT 1 button
                slot1_button = tk.Button(label, text="SLOT 1", command=lambda
                    x=get_relative_path(self.image_directory, self.images[index].name): write_html_file(browser, x, 1))
                slot1_button.place(relx=0.0, rely=1.0, anchor='sw')

                # Add SLOT 2 button
                slot2_button = tk.Button(label, text="SLOT 2", command=lambda
                    x=get_relative_path(self.image_directory, self.images[index].name): write_html_file(browser, x, 2))
                slot2_button.place(relx=1.0, rely=1.0, anchor='se')

                self.list_of_buttons.append(label)
                index += 1

            else:
                continue
            break

        # Set list_of_buttons attribute to update during filtering
        self.list_of_buttons = self.list_of_buttons

    def load_images_with_progress(self, browser, directory=None):
        # Clear existing buttons
        for button in self.list_of_buttons:
            button.destroy()
        self.list_of_buttons.clear()

        # Set image directory to the provided directory or the default directory
        if directory is None:
            directory = os.path.join(os.getcwd(), "card_images")
        self.image_directory = directory

        # Create default directory if it doesn't exist
        os.makedirs(self.image_directory, exist_ok=True)

        # Create CustomImage objects for each image file in the directory
        self.images = []

        # Create and pack the progress bar widget into the CustomFrame widget
        progress_bar = ttk.Progressbar(orient=tk.HORIZONTAL, length=200, mode='determinate')
        progress_bar.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        progress_bar.update()

        progress_bar["maximum"] = len(os.listdir(self.image_directory))
        for index, filename in enumerate(os.listdir(self.image_directory)):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                image = CustomImage(self.image_directory, filename)
                image.load_thumbnail(self.button_width, self.button_height)
                self.images.append(image)
                progress_bar["value"] = index + 1
                progress_bar.update()

        progress_bar.destroy()

        if len(self.images) == 0:
            messagebox.showinfo("No Images", f"{self.image_directory} directory is empty")
        else:
            rows, cols = self.calculate_grid_size()
            self.create_grid_of_buttons(rows, cols, browser)

            # Pack the buttons in the image_frame
            for button in self.list_of_buttons:
                button.pack(side="left", padx=self.padding, pady=self.padding)

    def filter_cards(self, event=None):
        search_text = self.search_field.get().lower()

        # Loop through all the labels and hide/show based on search text
        for button in self.list_of_buttons:
            label = button.winfo_children()[0]  # Get the label widget inside the button
            if search_text in label["text"].lower():
                button.pack(side=tk.LEFT, padx=self.padding, pady=self.padding)
            else:
                button.pack_forget()

        # Update the canvas scroll region to fit the filtered images
        # self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def reload_images(self, browser, directory):
        self.load_images_with_progress(browser, directory)  # Reload the images from the directory
        messagebox.showinfo("Reload", "Images reloaded successfully!")  # Show a message box to confirm reload
