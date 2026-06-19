import uuid
from tkinter import messagebox, ttk
import tkinter as tk

import pandas as pd
from sqlalchemy import text

import data
from config import make_logger
from db import get_connection
from gui import ControlPanelTable, StringField
from tools import Tool
from .._ui_components.invoice_template_form import InvoiceTemplateForm
from .._ui_components.invoice_item_table import InvoiceItemTable

logger = make_logger(__name__)


class InvoiceTemplateCreator(Tool):

    def __init__(self, master: tk.Tk):
        super().__init__(master, title="Invoice Template Creator")
        self._editing_id: str | None = None

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # ── Left: form + buttons ──────────────────────────────────────────────
        left = ttk.Frame(self)
        left.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nw")

        ttk.Label(left, text="Invoice Template", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        self._form = InvoiceTemplateForm(left)
        self._form.pack(padx=10, pady=10)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(padx=10, pady=5, anchor="w")
        self._save_btn = ttk.Button(btn_frame, text="Create", command=self._handle_save)
        self._save_btn.grid(row=0, column=0, padx=(0, 5))
        self._cancel_btn = ttk.Button(btn_frame, text="Clear", command=self._handle_cancel, style="Ghost.TButton")
        self._cancel_btn.grid(row=0, column=1)

        ttk.Separator(left, orient="horizontal").pack(fill="x", padx=10, pady=15)

        ttk.Label(left, text="Template Items", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(0, 0))
        self._items_label = ttk.Label(left, text="Select a template to edit items", foreground="gray")
        self._items_label.pack(anchor="w", padx=10, pady=(2, 6))

        item_btn_frame = ttk.Frame(left)
        item_btn_frame.pack(padx=10, pady=5, anchor="w")
        ttk.Button(item_btn_frame, text="+ Row", command=self._handle_add_row).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(item_btn_frame, text="- Row", command=self._handle_delete_row, style="Ghost.TButton").grid(row=0, column=1, padx=(0, 5))
        ttk.Button(item_btn_frame, text="Save Items", command=self._handle_save_items).grid(row=0, column=2)

        # ── Top-right: template table ─────────────────────────────────────────
        top_right = ttk.Frame(self)
        top_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        top_right.columnconfigure(0, weight=1)
        top_right.rowconfigure(0, weight=1)

        self._table = ControlPanelTable(top_right, title="Invoice Templates", columns={
            "InvoiceTemplateId":   {"is_hidden": True},
            "PayeeId":             {"is_hidden": True},
            "InvoiceTemplateName": {"justify": "left",   "width": 300},
            "PayeeName":           {"justify": "left",   "width": 250},
        })
        self._table.set_edit_command(self._handle_edit)
        self._table.set_delete_command(self._handle_delete)
        self._table.set_create_command(self._handle_cancel)
        self._table.grid(row=0, column=0, sticky="nsew")

        # ── Bottom-right: items table ─────────────────────────────────────────
        bottom_right = ttk.Frame(self)
        bottom_right.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="nsew")
        bottom_right.columnconfigure(0, weight=1)
        bottom_right.rowconfigure(0, weight=1)

        items_header = ttk.Frame(bottom_right)
        items_header.pack(fill="x")
        ttk.Label(items_header, text="Items", font=("Segoe UI", 11, "bold")).pack(side="left", pady=(4, 2))

        self._items_table = InvoiceItemTable(bottom_right)
        self._items_table.pack(fill="both", expand=True)

        self._refresh_table()

    # ── Data ──────────────────────────────────────────────────────────────────

    def _refresh_table(self):
        payee_names = [""] + data.Payee()["PayeeName"].tolist()
        self._form.payee_widget["values"] = payee_names
        self._form.payee_widget._all_values = payee_names

        df = data.InvoiceTemplates()
        for col in ("PayeeId", "PayeeName"):
            if col not in df.columns:
                df[col] = None
        df = df[["InvoiceTemplateId", "PayeeId", "InvoiceTemplateName", "PayeeName"]]
        self._table.data = df.fillna("")

    def _load_items(self, template_id: str):
        with get_connection("ldr") as conn:
            df = pd.read_sql_query(
                text(
                    "SELECT [DisplayOrder] AS [#], [CategoryDisplayName] AS [Category], "
                    "[Description], [Quantity], [Amount] "
                    "FROM [v_InvoiceTemplateItem] "
                    "WHERE [InvoiceTemplateId] = :id "
                    "ORDER BY [DisplayOrder]"
                ),
                conn, params={"id": template_id},
            )
        self._items_table.data = df

    def _clear_items(self):
        self._items_table.clear()

    # ── Template CRUD ─────────────────────────────────────────────────────────

    def _handle_save(self):
        form_data = self._form.get()
        name = form_data.get("template_name", "").strip()
        payee_name = form_data.get("payee", "").strip() or None

        if not name:
            messagebox.showwarning("Validation", "Template Name is required.")
            return

        payee_id = None
        if payee_name:
            payee_id = data.get_payee_id(payee_name)
            if payee_id is None:
                messagebox.showwarning("Validation", f"Unknown payee: '{payee_name}'")
                return

        try:
            with get_connection("ldr") as conn:
                if self._editing_id is None:
                    conn.execute(text(
                        "INSERT INTO [InvoiceTemplate] (InvoiceTemplateId, InvoiceTemplateName, PayeeId) "
                        "VALUES (:id, :name, :payee_id)"
                    ), {"id": str(uuid.uuid4()), "name": name, "payee_id": payee_id})
                else:
                    conn.execute(text(
                        "UPDATE [InvoiceTemplate] SET InvoiceTemplateName=:name, PayeeId=:payee_id "
                        "WHERE InvoiceTemplateId=:id"
                    ), {"id": self._editing_id, "name": name, "payee_id": payee_id})
            self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            logger.error("Failed to save InvoiceTemplate: %s", e)
            messagebox.showerror("Error", f"Failed to save Invoice Template:\n{e}")

    def _handle_edit(self, row: dict):
        self._editing_id = row["InvoiceTemplateId"]
        self._form.set({
            "template_name": row["InvoiceTemplateName"],
            "payee":         row.get("PayeeName") or "",
        })
        self._save_btn.config(text="Save")
        self._cancel_btn.config(text="Cancel")
        self._items_label.config(text=row["InvoiceTemplateName"], foreground="")
        self._load_items(self._editing_id)

    def _handle_delete(self, row: dict):
        template_id = row["InvoiceTemplateId"]
        name = row["InvoiceTemplateName"]
        if not messagebox.askyesno("Confirm Delete", f"Delete template '{name}' and all its items?"):
            return
        try:
            with get_connection("ldr") as conn:
                conn.execute(text("DELETE FROM [InvoiceTemplateItem] WHERE InvoiceTemplateId=:id"), {"id": template_id})
                conn.execute(text("DELETE FROM [InvoiceTemplate] WHERE InvoiceTemplateId=:id"), {"id": template_id})
            if self._editing_id == template_id:
                self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            logger.error("Failed to delete InvoiceTemplate: %s", e)
            messagebox.showerror("Error", f"Failed to delete Invoice Template.\n\n{e}")

    def _handle_cancel(self):
        self._editing_id = None
        self._form.clear()
        self._save_btn.config(text="Create")
        self._cancel_btn.config(text="Clear")
        self._items_label.config(text="Select a template to edit items", foreground="gray")
        self._clear_items()

    # ── Items CRUD ────────────────────────────────────────────────────────────

    def _handle_add_row(self):
        if self._editing_id is None:
            messagebox.showinfo("Info", "Save the template first before adding items.")
            return
        self._items_table.add_row()

    def _handle_delete_row(self):
        self._items_table.delete_row()

    def _handle_save_items(self):
        if self._editing_id is None:
            messagebox.showinfo("Info", "Select a template to save items for.")
            return

        rows = []
        for child in self._items_table.get_children():
            values = self._items_table.item(child, "values")
            cols = list(self._items_table["columns"])
            row = dict(zip(cols, values))
            rows.append(row)

        items = []
        for i, row in enumerate(rows):
            cat_display = str(row.get("Category", "")).strip()
            description = str(row.get("Description", "")).strip()
            quantity_raw = str(row.get("Quantity", "")).strip()
            amount_raw = str(row.get("Amount", "")).strip()

            if not cat_display:
                messagebox.showwarning("Validation", f"Row {i+1}: Category is required.")
                return
            if not description:
                messagebox.showwarning("Validation", f"Row {i+1}: Description is required.")
                return

            cat_id = data.get_category_id(cat_display)
            if cat_id is None:
                messagebox.showwarning("Validation", f"Row {i+1}: Unknown category '{cat_display}'")
                return

            try:
                quantity = float(quantity_raw) if quantity_raw else None
            except ValueError:
                messagebox.showwarning("Validation", f"Row {i+1}: Quantity must be a number.")
                return

            try:
                amount = float(amount_raw) if amount_raw else None
            except ValueError:
                messagebox.showwarning("Validation", f"Row {i+1}: Amount must be a number.")
                return

            items.append({
                "InvoiceTemplateId":     self._editing_id,
                "InvoiceTemplateItemId": str(uuid.uuid4()),
                "CategoryId":            str(cat_id),
                "Description":           description,
                "Quantity":              quantity,
                "Amount":                amount,
                "DisplayOrder":          i + 1,
            })

        try:
            with get_connection("ldr") as conn:
                conn.execute(
                    text("DELETE FROM [InvoiceTemplateItem] WHERE InvoiceTemplateId=:id"),
                    {"id": self._editing_id},
                )
                if items:
                    df = pd.DataFrame(items)
                    df.to_sql("InvoiceTemplateItem", conn, if_exists="append", index=False)
            messagebox.showinfo("Saved", "Template items saved.")
            self._load_items(self._editing_id)
        except Exception as e:
            logger.error("Failed to save InvoiceTemplateItems: %s", e)
            messagebox.showerror("Error", f"Failed to save template items:\n{e}")
