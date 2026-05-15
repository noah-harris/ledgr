import uuid
from tkinter import messagebox, ttk
import tkinter as tk

from sqlalchemy import text

import data
from config import make_logger
from db import get_connection
from gui import ControlPanelTable
from tools import Tool
from .._ui_components.invoice_item_category_form import InvoiceItemCategoryForm

logger = make_logger(__name__)


class InvoiceItemCategoryManager(Tool):

    def __init__(self, master: tk.Tk):
        super().__init__(master, title="Invoice Item Category Manager")
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        categories_tab = _CategoriesTab(notebook)
        remap_tab = _RemapTab(notebook)
        notebook.add(categories_tab, text="Categories")
        notebook.add(remap_tab, text="Remap Items")

        def _on_tab_change(_event):
            idx = notebook.index(notebook.select())
            if idx == 0:
                categories_tab._refresh_table()
            else:
                remap_tab._refresh_dropdowns()

        notebook.bind("<<NotebookTabChanged>>", _on_tab_change)


# ──────────────────────────────────────────────────────────────────────────────
# Categories tab
# ──────────────────────────────────────────────────────────────────────────────

class _CategoriesTab(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self._editing_id: str | None = None

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Left: form + buttons ──────────────────────────────────
        left = ttk.Frame(self)
        left.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        ttk.Label(left, text="Invoice Item Category", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        self._form = InvoiceItemCategoryForm(left)
        self._form.pack(padx=10, pady=10)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(padx=10, pady=5, anchor="w")
        self._save_btn = ttk.Button(btn_frame, text="Create", command=self._handle_save)
        self._save_btn.grid(row=0, column=0, padx=(0, 5))
        self._cancel_btn = ttk.Button(btn_frame, text="Clear", command=self._handle_cancel, style="Ghost.TButton")
        self._cancel_btn.grid(row=0, column=1)

        # ── Right: table ──────────────────────────────────────────
        right = ttk.Frame(self)
        right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        self._table = ControlPanelTable(right, title="Categories", columns={
            "CategoryId":          {"is_hidden": True},
            "Segment":             {"justify": "left",   "width": 120},
            "Category":            {"justify": "left",   "width": 160},
            "Subcategory":         {"justify": "left",   "width": 160},
            "CategoryDisplayName": {"justify": "left",   "width": 360},
            "Unit":                {"justify": "center", "width":  80},
            "DisplayOrder":        {"justify": "center", "width":  80},
        })
        self._table.set_edit_command(self._handle_edit)
        self._table.set_delete_command(self._handle_delete)
        self._table.set_create_command(self._handle_create)
        self._table.grid(row=0, column=0, sticky="nsew")

        self._refresh_table()

    def _refresh_table(self):
        cols = ["CategoryId", "Segment", "Category", "Subcategory", "CategoryDisplayName", "Unit", "DisplayOrder"]
        df = data.InvoiceItemCategory()[cols].sort_values(["Segment", "DisplayOrder"])
        self._table.data = df.fillna("")

    def _handle_save(self):
        form_data    = self._form.get()
        segment      = (form_data.get("segment") or "").strip()
        category     = (form_data.get("category") or "").strip()
        sub_category = (form_data.get("sub_category") or "").strip()
        unit         = (form_data.get("unit") or "").strip()
        display_order_s = (form_data.get("display_order") or "").strip()
        description  = (form_data.get("description") or "").strip() or None

        if not segment:
            messagebox.showwarning("Validation", "Segment is required.")
            return
        if not category:
            messagebox.showwarning("Validation", "Category is required.")
            return
        if not sub_category:
            messagebox.showwarning("Validation", "Sub Category is required.")
            return
        if not display_order_s:
            messagebox.showwarning("Validation", "Display Order is required.")
            return
        try:
            display_order = int(display_order_s)
        except ValueError:
            messagebox.showwarning("Validation", "Display Order must be a whole number.")
            return

        try:
            with get_connection("ldr") as conn:
                if self._editing_id is None:
                    conn.execute(text(
                        "INSERT INTO [InvoiceItemCategory] "
                        "(CategoryId, Segment, Category, SubCategory, Unit, DisplayOrder, Description) "
                        "VALUES (:id, :segment, :category, :sub_category, :unit, :display_order, :description)"
                    ), {
                        "id": str(uuid.uuid4()),
                        "segment": segment,
                        "category": category,
                        "sub_category": sub_category,
                        "unit": unit,
                        "display_order": display_order,
                        "description": description,
                    })
                else:
                    conn.execute(text(
                        "UPDATE [InvoiceItemCategory] SET "
                        "Segment=:segment, Category=:category, SubCategory=:sub_category, "
                        "Unit=:unit, DisplayOrder=:display_order, Description=:description "
                        "WHERE CategoryId=:id"
                    ), {
                        "id": self._editing_id,
                        "segment": segment,
                        "category": category,
                        "sub_category": sub_category,
                        "unit": unit,
                        "display_order": display_order,
                        "description": description,
                    })
            self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            logger.error("Failed to save InvoiceItemCategory: %s", e)
            messagebox.showerror("Error", f"Failed to save category:\n{e}")

    def _handle_create(self):
        self._handle_cancel()

    def _handle_cancel(self):
        self._editing_id = None
        self._form.clear()
        self._save_btn.config(text="Create")
        self._cancel_btn.config(text="Clear")

    def _handle_edit(self, row: dict):
        self._editing_id = row["CategoryId"]
        self._form.set({
            "segment":       row["Segment"],
            "category":      row["Category"],
            "sub_category":  row["Subcategory"],
            "unit":          row["Unit"],
            "display_order": str(row["DisplayOrder"]),
            "description":   row.get("Description"),
        })
        self._save_btn.config(text="Save")
        self._cancel_btn.config(text="Cancel")

    def _handle_delete(self, row: dict):
        category_id   = row["CategoryId"]
        display_name  = row["CategoryDisplayName"]
        if not messagebox.askyesno("Confirm Delete", f"Delete category '{display_name}'?"):
            return
        try:
            with get_connection("ldr") as conn:
                conn.execute(text("DELETE FROM [InvoiceItemCategory] WHERE CategoryId=:id"), {"id": category_id})
            if self._editing_id == category_id:
                self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            logger.error("Failed to delete InvoiceItemCategory: %s", e)
            messagebox.showerror("Error", f"Failed to delete category.\nIt may be in use by existing invoice items.\n\n{e}")


# ──────────────────────────────────────────────────────────────────────────────
# Remap tab
# ──────────────────────────────────────────────────────────────────────────────

class _RemapTab(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Left: controls ────────────────────────────────────────
        left = ttk.Frame(self)
        left.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        ttk.Label(left, text="Remap Invoice Items", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        form_frame = ttk.Frame(left)
        form_frame.pack(padx=10, pady=10, anchor="w")

        ttk.Label(form_frame, text="From Category:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self._from_var = tk.StringVar()
        self._from_combo = ttk.Combobox(form_frame, textvariable=self._from_var, state="readonly", width=50)
        self._from_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(form_frame, text="To Category:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self._to_var = tk.StringVar()
        self._to_combo = ttk.Combobox(form_frame, textvariable=self._to_var, state="readonly", width=50)
        self._to_combo.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ttk.Button(left, text="Remap", command=self._handle_remap).pack(padx=10, pady=5, anchor="w")

        # ── Right: info ────────────────────────────────────────────
        right = ttk.Frame(self)
        right.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        ttk.Label(
            right,
            text=(
                "Select a source and target category, then click Remap.\n\n"
                "All invoice items and invoice template items currently assigned\n"
                "to the source category will be reassigned to the target category.\n\n"
                "This action cannot be undone."
            ),
            justify="left",
            wraplength=320,
        ).pack(anchor="nw", pady=10)

        self._refresh_dropdowns()

    def _refresh_dropdowns(self):
        names = data.InvoiceItemCategory()["CategoryDisplayName"].tolist()
        names.sort()
        self._from_combo["values"] = names
        self._to_combo["values"] = names

    def _handle_remap(self):
        from_name = self._from_var.get().strip()
        to_name   = self._to_var.get().strip()

        if not from_name:
            messagebox.showwarning("Validation", "Please select a 'From' category.")
            return
        if not to_name:
            messagebox.showwarning("Validation", "Please select a 'To' category.")
            return
        if from_name == to_name:
            messagebox.showwarning("Validation", "'From' and 'To' categories must be different.")
            return

        from_id = data.get_category_id(from_name)
        to_id   = data.get_category_id(to_name)

        if not from_id or not to_id:
            messagebox.showerror("Error", "Could not resolve one or both category IDs.")
            return

        if not messagebox.askyesno(
            "Confirm Remap",
            f"Remap all invoice items from:\n  '{from_name}'\nto:\n  '{to_name}'?\n\nThis cannot be undone.",
        ):
            return

        try:
            with get_connection("ldr") as conn:
                r1 = conn.execute(
                    text("UPDATE [InvoiceItem] SET [CategoryId]=:to_id WHERE [CategoryId]=:from_id"),
                    {"to_id": to_id, "from_id": from_id},
                )
                r2 = conn.execute(
                    text("UPDATE [InvoiceTemplateItem] SET [CategoryId]=:to_id WHERE [CategoryId]=:from_id"),
                    {"to_id": to_id, "from_id": from_id},
                )
            total = r1.rowcount + r2.rowcount
            messagebox.showinfo(
                "Remap Complete",
                f"Remapped {total} record(s):\n"
                f"  Invoice items: {r1.rowcount}\n"
                f"  Template items: {r2.rowcount}",
            )
            self._from_var.set("")
            self._to_var.set("")
        except Exception as e:
            logger.error("Failed to remap InvoiceItemCategory: %s", e)
            messagebox.showerror("Error", f"Failed to remap:\n{e}")
