import tkinter as tk
from tkinter import ttk, messagebox
from functools import cached_property
from decimal import Decimal
from pathlib import Path
import re
import uuid
import pandas as pd

from db import get_connection
from gui import Modal, Table, ImageViewer, get_image_size_from_bytes
from resolve_image_bytes import resolve_image_bytes
from config import IMAGE_DIRECTORY
import data
from models import Invoice
from style import FONT, SUCCESS, DANGER
from tools._ui_components import InvoiceForm, InvoiceItemTable
from tools._ui_components.image_selector import ImageSelector


class InvoiceEditor(Modal):

    def __init__(self, master: tk.Tk, invoice_id: str):
        super().__init__(master, is_fullscreen=True)
        self._invoice_id = invoice_id
        self._invoice = Invoice(invoice_id)
        self._pending_image_id: str | None = self._invoice.ImageId
        self._image_viewer: ImageViewer | None = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_ui()
        self._prefill()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self):
        ttk.Label(self, text="Edit Invoice", style='Heading.TLabel').grid(
            row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w"
        )
        self.invoice_form.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nw")
        self.invoice_item_table.grid(row=1, column=1, padx=(0, 10), sticky="nsew")
        self._right_panel.grid(row=1, column=2, rowspan=2, padx=(0, 10), pady=(0, 10), sticky="nsew")

        ttk.Button(self, text="Save", command=self._save).grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )
        self._controls_frame.grid(row=2, column=1, sticky="w")
        self.invoice_item_table_total.grid(row=2, column=1, sticky="e", padx=(0, 10))

        self.bind("<Control-n>", lambda e: self.invoice_item_table.add_row(values=None))
        self.bind("<Delete>",    lambda e: self.invoice_item_table.delete_row())
        self.invoice_item_table.bind("<<RowChange>>", lambda e: self._update_total())
        self.invoice_form.amount_widget.bind("<KeyRelease>", lambda e: self._update_total())
        self.bind("<F1>", self.invoice_item_table._cat_on_f1)
        self.bind("<F2>", lambda e: self.invoice_item_table._open_editor_by_col("Description"))
        self.bind("<F3>", lambda e: self.invoice_item_table._open_editor_by_col("Quantity"))
        self.bind("<F4>", lambda e: self.invoice_item_table._open_editor_by_col("Amount"))

    def _prefill(self):
        inv = self._invoice
        self.invoice_form.set({
            "payee":          inv.PayeeName,
            "invoice_date":   inv.InvoiceDate,
            "due_date":       inv.DueDate,
            "invoice_number": inv.InvoiceNumber,
            "amount":         inv.Amount,
            "description":    inv.InvoiceDescription,
            "start_date":     inv.StartDate,
            "end_date":       inv.EndDate,
        })

        if inv.InvoiceItems is not None and not inv.InvoiceItems.empty:
            items = inv.InvoiceItems.rename(columns={"Qty": "Quantity", "Amt": "Amount"})
            items = items.drop(columns=["InvoiceId"], errors="ignore")
            items = items[["#", "Category", "Description", "Quantity", "Amount"]]
            self.invoice_item_table.data = items

        self._update_total()
        self._load_image_viewer(inv.ImageFileName)

    # ------------------------------------------------------------------
    # Cached properties — core widgets
    # ------------------------------------------------------------------

    @cached_property
    def invoice_form(self) -> InvoiceForm:
        return InvoiceForm(self)

    @cached_property
    def invoice_item_table(self) -> InvoiceItemTable:
        def _amount_validator(value) -> str:
            try:
                cleaned = str(value).strip()
                if not re.fullmatch(r"-?(?:\d*\.\d{1,2}|\d+)", cleaned):
                    raise ValueError
                return f"{Decimal(cleaned):.2f}"
            except ValueError:
                raise ValueError("Expected format: 0.00")

        def _quantity_validator(value) -> str:
            try:
                cleaned = str(value).strip()
                if not re.fullmatch(r"-?(?:\d*\.\d{1,3}|\d+)", cleaned):
                    raise ValueError
                return f"{Decimal(cleaned):.3f}"
            except ValueError:
                raise ValueError("Expected format: 0.000")

        table = InvoiceItemTable(self)
        table.set_validator("Amount", _amount_validator)
        table.set_validator("Quantity", _quantity_validator)
        return table

    @cached_property
    def invoice_item_table_total(self) -> ttk.Label:
        self._total_var = tk.StringVar(value="0.00")
        return ttk.Label(self, textvariable=self._total_var, font=(FONT, 24, 'bold'))

    @cached_property
    def _controls_frame(self) -> ttk.Frame:
        frame = ttk.Frame(self)
        ttk.Button(frame, text="Add Item", command=self.invoice_item_table.add_row).grid(row=0, column=0, padx=5)
        ttk.Button(frame, text="Delete Item", command=self.invoice_item_table.delete_row, style='Danger.TButton').grid(row=0, column=1, padx=(0, 5))
        return frame

    # ------------------------------------------------------------------
    # Right panel — image + linked payments
    # ------------------------------------------------------------------

    @cached_property
    def _right_panel(self) -> ttk.Frame:
        frame = ttk.Frame(self)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        self._image_section(frame).grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self._linked_items_section(frame).grid(row=1, column=0, sticky="ew")
        return frame

    def _image_section(self, parent) -> ttk.LabelFrame:
        lf = ttk.LabelFrame(parent, text="Image", padding=8)
        lf.grid_columnconfigure(0, weight=1)
        lf.grid_rowconfigure(0, weight=1)

        self._image_viewer = ImageViewer(lf, show_nav_buttons=False)
        self._image_viewer.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self._image_name_var = tk.StringVar(value=self._invoice.ImageFileName or "No image assigned")
        ttk.Label(lf, textvariable=self._image_name_var, wraplength=220, justify="left").grid(
            row=1, column=0, sticky="w", pady=(6, 4)
        )
        ttk.Button(lf, text="Change Image", command=self._change_image).grid(
            row=2, column=0, sticky="w"
        )
        return lf

    def _linked_items_section(self, parent) -> ttk.LabelFrame:
        lf = ttk.LabelFrame(parent, text="Linked Payments", padding=8)
        lf.grid_columnconfigure(0, weight=1)

        self._linked_table = Table(lf, columns={
            "Account":         {"justify": "left", "width": 130},
            "Date":            {"justify": "center", "width": 85},
            "Amount":          {"justify": "right",  "width": 70},
            "StatementItemId": {"is_hidden": True},
        }, visible_rows=6)
        self._linked_table.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        self._refresh_linked_items()

        btn_frame = ttk.Frame(lf)
        btn_frame.grid(row=1, column=0, sticky="w")
        ttk.Button(btn_frame, text="Link Item",   command=self._open_link_modal).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(btn_frame, text="Unlink",      command=self._unlink_selected, style='Danger.TButton').grid(row=0, column=1)
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
    # Statement item link / unlink
    # ------------------------------------------------------------------

    def _refresh_linked_items(self):
        df = data.v_DisplayStatementItem()
        df = df[df['InvoiceId'] == self._invoice_id.upper()]
        if df.empty:
            self._linked_table.data = pd.DataFrame(columns=["Account", "Date", "Amount", "StatementItemId"])
        else:
            self._linked_table.data = pd.DataFrame({
                "Account":         df['AccountOrganizationName'],
                "Date":            df['TransactionDate'].astype(str),
                "Amount":          df['Amount'],
                "StatementItemId": df['StatementItemId'],
            })

    def _open_link_modal(self):
        modal = Modal(self)
        modal.grid_columnconfigure(0, weight=1)
        modal.grid_rowconfigure(1, weight=1)

        search_var = tk.StringVar(value=self._invoice.PayeeName or "")
        search_frame = ttk.Frame(modal)
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        ttk.Label(search_frame, text="Payee filter:").pack(side="left", padx=(0, 6))
        ttk.Entry(search_frame, textvariable=search_var, width=30).pack(side="left")

        result_table = Table(modal, columns={
            "Account":         {"justify": "left",   "width": 150},
            "Payee":           {"justify": "left",   "width": 130},
            "Date":            {"justify": "center", "width": 90},
            "Amount":          {"justify": "right",  "width": 70},
            "StatementItemId": {"is_hidden": True},
        }, visible_rows=20)
        result_table.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 4))

        def _load(*_):
            df = data.v_StatementItem()
            df = df[df['InvoiceId'].isna()]
            payee = search_var.get().strip().upper()
            if payee:
                df = df[df['Payee'].str.upper().str.contains(payee, na=False)]
            result_table.data = pd.DataFrame({
                "Account":         df['Account'],
                "Payee":           df['Payee'],
                "Date":            df['TransactionDate'].astype(str),
                "Amount":          df['Amount'],
                "StatementItemId": df['StatementItemId'],
            })

        search_var.trace_add("write", _load)
        _load()

        def _do_link():
            row = result_table.get_selected_row()
            if not row:
                return
            with get_connection("ldr") as conn:
                data.update_statement_item_invoice_id(conn, self._invoice_id, row["StatementItemId"])
            modal.close()
            self._refresh_linked_items()

        result_table.bind("<Double-1>", lambda e: _do_link())
        btn_frame = ttk.Frame(modal)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        ttk.Button(btn_frame, text="Link",   command=_do_link).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="Cancel", command=modal.close).pack(side="left")

    def _unlink_selected(self):
        row = self._linked_table.get_selected_row()
        if not row:
            return
        if not messagebox.askyesno("Confirm unlink", "Remove this statement item from the invoice?"):
            return
        with get_connection("ldr") as conn:
            data.unlink_statement_item_from_invoice(conn, row["StatementItemId"])
        self._refresh_linked_items()

    # ------------------------------------------------------------------
    # Total helpers
    # ------------------------------------------------------------------

    def _table_total(self) -> Decimal:
        return round(Decimal(str(
            pd.to_numeric(self.invoice_item_table.data["Amount"], errors="coerce").fillna(0).sum()
        )), 2)

    def _invoice_total(self) -> Decimal:
        raw = self.invoice_form.amount_widget.get()
        try:
            return round(Decimal(raw), 2)
        except Exception:
            return Decimal("0.00")

    def _totals_match(self) -> bool:
        return self._table_total() == self._invoice_total()

    def _update_total(self):
        total = self._table_total()
        self._total_var.set(f"{total:.2f}")
        self.invoice_item_table_total.configure(
            foreground=SUCCESS if self._totals_match() else DANGER
        )

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save(self):
        inv = self.invoice_form.get()

        if not self._totals_match():
            messagebox.showerror("Total mismatch", "The invoice item total does not match the invoice amount. Adjust before saving.")
            return
        if not inv['payee']:
            messagebox.showerror("Missing payee", "Please specify a payee.")
            return
        if not inv['invoice_date']:
            messagebox.showerror("Missing date", "Please specify the invoice date.")
            return
        if not inv['amount']:
            messagebox.showerror("Missing amount", "Please specify the invoice total amount.")
            return

        invoice_data = {
            "InvoiceId":     self._invoice_id,
            "PayeeId":       data.get_payee_id(inv['payee']),
            "InvoiceDate":   inv['invoice_date'],
            "DueDate":       inv['due_date'],
            "InvoiceNumber": inv['invoice_number'],
            "Amount":        inv['amount'],
            "Description":   inv['description'],
            "StartDate":     inv['start_date'],
            "EndDate":       inv['end_date'],
            "ImageId":       self._pending_image_id,
        }

        invoice_items = self.invoice_item_table.data.copy()
        invoice_items = invoice_items.rename(columns={"#": "DisplayOrder"})
        invoice_items['InvoiceId'] = self._invoice_id
        invoice_items['CategoryId'] = invoice_items['Category'].apply(
            lambda x: data.get_category_id(x) if pd.notna(x) else None
        )
        invoice_items = invoice_items.drop(columns=['Category'])
        invoice_items['InvoiceItemId'] = [str(uuid.uuid4()) for _ in range(len(invoice_items))]

        try:
            with get_connection("ldr") as conn:
                data.update_invoice(conn, invoice_data, invoice_items)
            messagebox.showinfo("Saved", "Invoice updated successfully.")
            self.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice: {str(e)}")
