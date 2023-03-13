import tkinter as tk
from tkinter import filedialog

from gui.custom_frame import CustomFrame


class CustomWindow(tk.Tk):
    def __init__(self, browser, title="Custom Window", width=800, height=500,
                 resizable=(True, True), frames=None, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.browser = browser
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(resizable[0], resizable[1])
        self.canvas = None
        self.frames_pane = tk.Frame(self)
        if frames is None:
            frames = []
        self.frames = frames
        self.create_widgets(self.browser)

    def create_widgets(self, browser):
        # Create a frame for the buttons
        window_buttons = tk.Frame(self)
        window_buttons.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a button to add a new frame and add it to the buttons frame
        add_frame_button = tk.Button(window_buttons, text="Add Frame", command=self.add_frame)
        add_frame_button.pack(fill="both", pady=10, padx=10)

        # Create a container frame to hold all custom frames
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.frames_pane = tk.Frame(self.canvas)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.frames_pane, anchor="nw")
        self.frames_pane.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Create a default frame and add it to the container frame
        default_frame = CustomFrame(self.frames_pane, browser=self.browser)
        # default_frame.create_widgets(self)
        # default_frame.load_images_with_progress(frame=default_frame)
        default_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Use after_idle to add the default frame to the container frame after the window is fully initialized
        self.after_idle(lambda: default_frame.pack_forget())
        self.after_idle(lambda: default_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True))

    def add_frame(self):
        # Open a dialog box to select a directory
        directory = filedialog.askdirectory()

        if directory:
            # Create a new frame and add it to the container frame using the new directory
            new_frame = CustomFrame(self.frames_pane, browser=self.browser, image_directory=directory)
            new_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
