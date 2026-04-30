from functools import cached_property

from tools import Tool
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

class OrganizationCreator(Tool):
    def __init__(self, master:tk.Tk):
        super().__init__(master)