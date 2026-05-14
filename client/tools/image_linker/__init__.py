import pandas as pd
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
from resolve_image_bytes import resolve_image_bytes


class ImageLinker(Tool):

    def __init__(self, master):
        super().__init__(master, title="Sort Images")

        self._syncing_table = False

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        # Order matters: viewer → right panel (creates table widgets) → queue (loads data)
        self.image_viewer.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self._right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        self.image_queue  # initialise queue + load first image
        self._refresh_queue_table()  # populate table now that queue exists

        self.image_viewer.next_image_button.config(command=self._handle_next)
        self.image_viewer.prev_image_button.config(command=self._handle_prev)
        self.bind("<Up>", self.image_viewer._prev_page)
        self.bind("<Down>", self.image_viewer._next_page)

        self._sync_table_to_queue()

    # ── Viewer ────────────────────────────────────────────────

    @cached_property
    def image_viewer(self) -> ImageViewer:
        return ImageViewer(self, canvas_size=(800, 800))

    # ── Queue ─────────────────────────────────────────────────

    @cached_property
    def image_queue(self) -> ImageQueue:
        raw_queue = data.UnmatchedImages()
        queue = raw_queue.to_dict(orient="records")
        for record in queue:
            filename = record["ImageFileName"]
            if filename:
                record["filetype"] = Path(filename).suffix.lstrip(".")
                record["filename_stem"] = Path(filename).stem
                record["get_bytes"] = (lambda fn: lambda: resolve_image_bytes(f"{IMAGE_DIRECTORY}/{fn}"))(filename)
            else:
                record["filetype"] = None
                record["filename_stem"] = None
                record["get_bytes"] = None
        q = ImageQueue(self.image_viewer, queue)
        q._refresh_viewer()
        return q

    # ── Right panel ───────────────────────────────────────────

    @cached_property
    def _right_panel(self) -> ttk.Frame:
        panel = ttk.Frame(self, style="Surface.TFrame")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        # ── Content Type section ──────────────────────────────
        ct_frame = ttk.Frame(panel, style="Surface.TFrame")
        ct_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        ct_frame.columnconfigure(0, weight=1)

        ttk.Label(ct_frame, text="Content Type", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        self._content_type_var = tk.StringVar()
        combobox = ttk.Combobox(
            ct_frame,
            values=data.ImageContentType()["ContentType"].tolist(),
            textvariable=self._content_type_var,
            state="readonly",
            width=36,
        )
        combobox.bind("<<ComboboxSelected>>", self._handle_content_type_change)
        combobox.grid(row=1, column=0, sticky="ew")

        # ── Queue section ─────────────────────────────────────
        q_frame = ttk.Frame(panel, style="Surface.TFrame")
        q_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=6)
        q_frame.columnconfigure(0, weight=1)
        q_frame.rowconfigure(1, weight=1)

        header = ttk.Frame(q_frame, style="Surface.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Image Queue", style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        self._queue_count_var = tk.StringVar()
        ttk.Label(header, textvariable=self._queue_count_var, style="Subheading.TLabel").grid(
            row=0, column=1, sticky="e"
        )

        self.image_queue_table = Table(
            q_frame,
            columns={
                "ImageId":       {"is_hidden": True},
                "ImageFileName": {"justify": "left", "width": 460},
            },
        )
        self.image_queue_table.grid(row=1, column=0, sticky="nsew")
        self.image_queue_table.bind("<<TreeviewSelect>>", self._handle_queue_table_select)

        # ── Sort buttons ──────────────────────────────────────
        btn_frame = ttk.Frame(panel, style="Surface.TFrame")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(6, 12))

        ttk.Button(btn_frame, text="Orphan", style="Danger.TButton", command=self._handle_orphan).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(btn_frame, text="Skip", style="Ghost.TButton", command=self._handle_skip).grid(
            row=0, column=1
        )

        return panel

    # ── Queue helpers ─────────────────────────────────────────

    def _refresh_queue_table(self):
        rows = [
            {"ImageId": r["ImageId"], "ImageFileName": r["ImageFileName"]}
            for r in self.image_queue.queue
        ]
        df = (
            pd.DataFrame(rows)
            if rows
            else pd.DataFrame(columns=["ImageId", "ImageFileName"])
        )
        self.image_queue_table.data = df
        n = len(rows)
        self._queue_count_var.set(f"{n} remaining")

    def _sync_table_to_queue(self):
        self._syncing_table = True
        try:
            current = self.image_queue.get_current()
            if not current:
                return
            cid = str(current.get("ImageId", ""))
            for item_id in self.image_queue_table.get_children():
                vals = self.image_queue_table.item(item_id)["values"]
                if str(vals[0]) == cid:
                    self.image_queue_table.selection_set(item_id)
                    self.image_queue_table.see(item_id)
                    break
        finally:
            self._syncing_table = False

    def _remove_image(self):
        self.image_queue.remove_current()
        self._refresh_queue_table()
        self._sync_table_to_queue()

    # ── Navigation ────────────────────────────────────────────

    def _handle_next(self):
        self.image_queue.next()
        self._sync_table_to_queue()

    def _handle_prev(self):
        self.image_queue.prev()
        self._sync_table_to_queue()

    # ── Table selection ───────────────────────────────────────

    def _handle_queue_table_select(self, event=None):
        if self._syncing_table:
            return
        row = self.image_queue_table.get_selected_row()
        if row is None:
            return
        selected_id = str(row.get("ImageId", ""))
        for i, item in enumerate(self.image_queue.queue):
            if str(item.get("ImageId")) == selected_id:
                self.image_queue.index = i
                break

    # ── Sort actions ──────────────────────────────────────────

    def _handle_orphan(self):
        image_id = self.image_viewer.info.get("ImageId")
        if not image_id:
            return
        with get_connection("ldr") as conn:
            conn.execute(
                text("UPDATE [ImageSort] SET [StatusType] = 'o' WHERE [ImageId] = :image_id"),
                {"image_id": image_id},
            )
        logger.debug("Image marked as orphan")
        self._remove_image()

    def _handle_skip(self):
        image_id = self.image_viewer.info.get("ImageId")
        if not image_id:
            return
        with get_connection("ldr") as conn:
            conn.execute(
                text("UPDATE [ImageSort] SET [StatusType] = 's' WHERE [ImageId] = :image_id"),
                {"image_id": image_id},
            )
        logger.debug("Image marked as skipped")
        self._remove_image()

    # ── Content type routing ──────────────────────────────────

    def _handle_content_type_change(self, event):
        match self._content_type_var.get():
            case "ACCOUNT TRANSFER":
                AccountTransfer(self, self.image_queue)
            case "INVOICE":
                Invoice(self, self.image_queue)
            case "STATEMENT":
                image_id = self.image_queue.get_current().get("ImageId")
                if image_id:
                    StatementLoader(self, Image(ImageId=image_id))
            case "METHOD":
                pass
            case "TRANSACTION":
                StatementItem(self, self.image_queue, "TRANSACTION")
            case "RECEIPT":
                StatementItem(self, self.image_queue, "RECEIPT")
