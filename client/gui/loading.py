import tkinter as tk
from tkinter import ttk
from style import BACKGROUND

class LoadingWindow:
    def __init__(self, master, message="Loading..."):
        self.master = master
        self.message = message
        self.window = tk.Toplevel(master)
        self.window.title("Loading")
        self.window.state("zoomed")
        self.window.resizable(False, False)
        self.window.configure(bg=BACKGROUND)
        self.label = ttk.Label(self.window, text=message)
        self.label.pack(expand=True)
        self.window.transient(self.master)
        self.window.grab_set()
        self.window.update()

    def __enter__(self):
        self.window.deiconify()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.window.destroy()