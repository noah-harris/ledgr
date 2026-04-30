import tkinter as tk
from tkinter import ttk
from gui import Modal, Table
import data
from models import Image


class ImageSelector(Modal):

    def __init__(self, master):
        super().__init__(master, background_color="white", border_thickness=2, border_color="black")
        self._selected_image: Image = None
        self._all_images = data.UnmatchedImages()

        ttk.Label(self, text="Select Image", font=("", 12, "bold")).pack(pady=(10, 5))

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search)
        ttk.Entry(self, textvariable=self._search_var, width=50).pack(padx=10, pady=(0, 5))

        self._table = Table(self, columns={
            "ImageId":      {"is_hidden": True},
            "ImageFileName":{"justify": "left",   "width": 450},
            "ContentType":  {"justify": "center",  "width": 130},
            "StatusName":   {"justify": "center",  "width": 100},
        }, visible_rows=25)
        self._table.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        self._table.data = self._all_images
        self._table.bind("<Double-1>", self._handle_select)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=(0, 10))
        ttk.Button(btn_frame, text="Select", command=self._handle_select).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.close).grid(row=0, column=1, padx=5)

    @property
    def selected_image(self) -> Image | None:
        return self._selected_image

    def _on_search(self, *_):
        query = self._search_var.get().lower()
        if not query:
            self._table.data = self._all_images
        else:
            filtered = self._all_images[
                self._all_images["ImageFileName"].str.lower().str.contains(query, na=False)
            ]
            self._table.data = filtered

    def _handle_select(self, event=None):
        row = self._table.get_selected_row()
        if row is not None:
            self._selected_image = Image(ImageId=row["ImageId"])
            self.close()
