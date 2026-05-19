import tkinter as tk
from tkinter import ttk, messagebox
from functools import cached_property
from pathlib import Path

from db import get_connection
from gui import Modal, ImageViewer
from resolve_image_bytes import resolve_image_bytes
from config import IMAGE_DIRECTORY
import data
from models import StatementItem
from tools._ui_components import StatementItemForm
from tools._ui_components.image_selector import ImageSelector


class StatementItemEditor(Modal):

    def __init__(self, master: tk.Tk, statement_item_id: str):
        super().__init__(master, is_fullscreen=True)
        self._statement_item_id = statement_item_id
        self._item = StatementItem(statement_item_id)
        self._pending_image_id: str | None = self._item.ImageId
        self._image_viewer: ImageViewer | None = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_ui()
        self._prefill()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self):
        ttk.Label(self, text="Edit Statement Item", style='Heading.TLabel').grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w"
        )
        self.statement_item_form.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nw")
        self._right_panel.grid(row=1, column=1, padx=(0, 10), pady=(0, 10), sticky="nsew")
        ttk.Button(self, text="Save", command=self._save).grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )

    def _prefill(self):
        item = self._item
        method_display_name = data.get_method_display_name(self._statement_item_id)
        self.statement_item_form.set({
            "payee":            item.PayeeName,
            "method":           method_display_name,
            "transaction_date": item.TransactionDate,
            "post_date":        item.PostDate,
            "reference_number": item.ReferenceNumber,
            "amount":           item.Amount,
            "description":      item.StatementItemDescription,
        })
        self._load_image_viewer(item.ImageFileName)

    # ------------------------------------------------------------------
    # Cached properties — core widgets
    # ------------------------------------------------------------------

    @cached_property
    def statement_item_form(self) -> StatementItemForm:
        return StatementItemForm(self)

    @cached_property
    def _right_panel(self) -> ttk.Frame:
        frame = ttk.Frame(self)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        self._image_section(frame).grid(row=0, column=0, sticky="nsew")
        return frame

    def _image_section(self, parent) -> ttk.LabelFrame:
        lf = ttk.LabelFrame(parent, text="Receipt Image", padding=8)
        lf.grid_columnconfigure(0, weight=1)
        lf.grid_rowconfigure(0, weight=1)

        self._image_viewer = ImageViewer(lf, show_nav_buttons=False)
        self._image_viewer.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self._image_name_var = tk.StringVar(value=self._item.ImageFileName or "No image assigned")
        ttk.Label(lf, textvariable=self._image_name_var, wraplength=220, justify="left").grid(
            row=1, column=0, sticky="w", pady=(6, 4)
        )
        ttk.Button(lf, text="Change Image", command=self._change_image).grid(
            row=2, column=0, sticky="w"
        )
        return lf

    # ------------------------------------------------------------------
    # Image helpers
    # ------------------------------------------------------------------

    def _load_image_viewer(self, image_filename: str | None):
        if not image_filename:
            self._image_viewer.show_placeholder("No image assigned")
            return
        img_bytes = resolve_image_bytes(f"{IMAGE_DIRECTORY}/{image_filename}")
        if img_bytes is None:
            self._image_viewer.show_placeholder("Image unavailable")
            return
        filetype = Path(image_filename).suffix.lstrip(".")
        stem = Path(image_filename).stem
        self._image_viewer.load_from_bytes(img_bytes, filetype, stem)

    def _change_image(self):
        selector = ImageSelector(self, show_all=True)
        self.wait_window(selector)
        img = selector.selected_image
        if img:
            self._pending_image_id = img.ImageId
            self._image_name_var.set(img.ImageFileName or str(img.ImageId))
            self._load_image_viewer(img.ImageFileName)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save(self):
        form = self.statement_item_form.get()

        if not form['payee']:
            messagebox.showerror("Missing payee", "Please specify a payee.")
            return
        if not form['transaction_date']:
            messagebox.showerror("Missing date", "Please specify the transaction date.")
            return
        if not form['amount']:
            messagebox.showerror("Missing amount", "Please specify the amount.")
            return

        payee_id = data.get_payee_id(form['payee'])
        method_id = data.get_method_id(form['method']) if form['method'] else None

        item_data = {
            "StatementItemId": self._statement_item_id,
            "PayeeId":         payee_id,
            "MethodId":        method_id,
            "TransactionDate": form['transaction_date'],
            "PostDate":        form['post_date'].date() if form['post_date'] else None,
            "ReferenceNumber": form['reference_number'],
            "Amount":          form['amount'],
            "Description":     form['description'] or "",
            "ImageId":         self._pending_image_id,
        }

        try:
            with get_connection("ldr") as conn:
                data.update_statement_item(conn, item_data)
            messagebox.showinfo("Saved", "Statement item updated successfully.")
            self.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
