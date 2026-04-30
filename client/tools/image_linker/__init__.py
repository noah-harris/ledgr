from tools import Tool
from functools import cached_property
from pathlib import Path
from gui import ImageViewer, ImageQueue, Table
from config import *
import data
import tkinter as tk
from tkinter import ttk
from .statement_item import StatementItem
from .invoice import Invoice
from .account_transfer import AccountTransfer
from db import get_connection
from sqlalchemy import text
from ..statement_loader import StatementLoader
from models import Image

class ImageLinker(Tool):

    def __init__(self, master):
        super().__init__(master, title="Image Linker")
        self.content_type_frame.grid(row=0, column=0)
        self.image_viewer.grid(row=1, column=0)
        self.image_queue
        self.image_queue_table.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.sort_button_frame.grid(row=2, column=0, columnspan=2)
        self.bind("<Up>", self.image_viewer._prev_page)
        self.bind("<Down>", self.image_viewer._next_page)


    @cached_property
    def image_viewer(self) -> ImageViewer:
        image_viewer = ImageViewer(self, canvas_size=(800,800), )
        image_viewer.next_image_button.config(command=lambda: self.image_queue.next())
        image_viewer.prev_image_button.config(command=lambda: self.image_queue.prev())
        return image_viewer
    

    @cached_property
    def image_queue(self) -> ImageQueue:
        raw_queue = data.UnmatchedImages()
        queue = raw_queue.to_dict(orient="records")
        for record in queue:
            filename = record["ImageFileName"]
            if filename:
                record["filetype"] = Path(filename).suffix.lstrip(".")
                record["filename_stem"] = Path(filename).stem
                record["get_bytes"] = (lambda fn: lambda: fetch_image_bytes(fn))(filename)
            else:
                record["filetype"] = None
                record["filename_stem"] = None
                record["get_bytes"] = None
        image_queue = ImageQueue(self.image_viewer, queue)
        image_queue._refresh_viewer()
        return image_queue

    
    @cached_property
    def content_type_frame(self):
        self._content_type_var = tk.StringVar()
        frame = ttk.Frame(self)
        ttk.Label(frame, text="Content Type:").pack()        
        combobox = ttk.Combobox(frame, values= data.ImageContentType()['ContentType'].tolist(), textvariable=self._content_type_var, state="readonly")
        combobox.bind("<<ComboboxSelected>>", self._handle_content_type_change)
        combobox.pack()
        return frame


    @cached_property
    def sort_button_frame(self):
        
        def _handle_orphan():
            with get_connection() as conn:
                conn.execute(text("UPDATE [ImageSort] SET [StatusType] = 'o' WHERE [ImageId] = :image_id"), {"image_id": self.image_viewer.info["ImageId"]})
            logger.debug("Image marked as orphan")
            self._remove_image()

        def _handle_skip():
            with get_connection() as conn:
                conn.execute(text("UPDATE [ImageSort] SET [StatusType] = 's' WHERE [ImageId] = :image_id"), {"image_id": self.image_viewer.info["ImageId"]})
            logger.debug("Image marked as skipped")
            self._remove_image()

        frame = ttk.Frame(self)
        orphan_button = ttk.Button(frame, text="Orphan", command=_handle_orphan)
        skip_button = ttk.Button(frame, text="Skip", command=_handle_skip)

        orphan_button.grid(row=0, column=0, padx=10, pady=0)
        skip_button.grid(row=0, column=1, padx=10, pady=0)
        return frame
    
    @cached_property
    def image_queue_table(self):
        tbl = Table(self, columns={"ImageId": {'justify':'center','width':250}, "ImageFileName": {'justify':'left', 'width':500}})
        tbl.data = data.UnmatchedImages()
        return tbl
    

    def _handle_content_type_change(self, event):
        match self._content_type_var.get():

            case 'ACCOUNT TRANSFER':
                AccountTransfer(self, self.image_queue)
    
            case 'INVOICE':
                Invoice(self, self.image_queue)

            case 'STATEMENT':
                image_id = self.image_queue.get_current().get('ImageId')
                if image_id:
                    StatementLoader(self, Image(ImageId=image_id))

            case 'METHOD':
                pass

            case 'TRANSACTION':
                StatementItem(self, self.image_queue, 'TRANSACTION')

            case 'RECEIPT':
                StatementItem(self, self.image_queue, 'RECEIPT')


    def _remove_image(self):
        self.image_queue.remove_current()