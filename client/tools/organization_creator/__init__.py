import uuid
from tkinter import messagebox, ttk
import tkinter as tk

from sqlalchemy import text

import data
from config import make_logger
from db import get_connection
from gui import ControlPanelTable
from tools import Tool
from .._ui_components.organization_form import OrganizationForm
from .._ui_components.organization_type_form import OrganizationTypeForm

logger = make_logger(__name__)


class OrganizationCreator(Tool):

    def __init__(self, master: tk.Tk):
        super().__init__(master, title="Organization Manager")
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        orgs_tab = _OrganizationsTab(notebook)
        types_tab = _OrganizationTypesTab(notebook)
        notebook.add(orgs_tab, text="Organizations")
        notebook.add(types_tab, text="Organization Types")

        def _on_tab_change(_event):
            idx = notebook.index(notebook.select())
            if idx == 0:
                orgs_tab._refresh_table()
            else:
                types_tab._refresh_table()

        notebook.bind("<<NotebookTabChanged>>", _on_tab_change)


# ──────────────────────────────────────────────────────────────────────────────
# Organizations tab
# ──────────────────────────────────────────────────────────────────────────────

class _OrganizationsTab(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self._editing_id: str | None = None

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Left: form + buttons ──────────────────────────────────
        left = ttk.Frame(self)
        left.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        ttk.Label(left, text="Organization", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        self._form = OrganizationForm(left)
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

        self._table = ControlPanelTable(right, title="Organizations", columns={
            "OrganizationId":       {"is_hidden": True},
            "OrganizationName":     {"justify": "left",   "width": 200},
            "OrganizationTypeName": {"justify": "left",   "width": 160},
            "Segment":              {"justify": "center", "width": 120},
            "Description":          {"justify": "left",   "width": 280},
        })
        self._table.set_edit_command(self._handle_edit)
        self._table.set_delete_command(self._handle_delete)
        self._table.set_create_command(self._handle_create)
        self._table.grid(row=0, column=0, sticky="nsew")

        self._refresh_table()

    def _refresh_table(self):
        types = data.OrganizationTypes()["OrganizationTypeName"].tolist()
        cb = self._form.org_type_widget
        cb["values"] = types
        cb._all_values = types

        df = data.Organizations()[["OrganizationId", "OrganizationName", "OrganizationTypeName", "Segment", "Description"]]
        self._table.data = df.fillna("")

    def _handle_save(self):
        form_data = self._form.get()
        name = form_data.get("name")
        org_type_name = form_data.get("org_type")
        description = form_data.get("description")

        if not name:
            messagebox.showwarning("Validation", "Organization Name is required.")
            return
        if not org_type_name:
            messagebox.showwarning("Validation", "Organization Type is required.")
            return

        types_df = data.OrganizationTypes()
        match = types_df[types_df["OrganizationTypeName"] == org_type_name]
        if match.empty:
            messagebox.showwarning("Validation", f"Unknown Organization Type: '{org_type_name}'")
            return
        type_id = str(match.iloc[0]["OrganizationTypeId"])

        try:
            with get_connection("ldr") as conn:
                if self._editing_id is None:
                    conn.execute(text(
                        "INSERT INTO [Organization] (OrganizationId, OrganizationName, OrganizationTypeId, Description) "
                        "VALUES (:id, :name, :type_id, :desc)"
                    ), {"id": str(uuid.uuid4()), "name": name, "type_id": type_id, "desc": description})
                else:
                    conn.execute(text(
                        "UPDATE [Organization] SET OrganizationName=:name, OrganizationTypeId=:type_id, Description=:desc "
                        "WHERE OrganizationId=:id"
                    ), {"id": self._editing_id, "name": name, "type_id": type_id, "desc": description})
            self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            logger.error("Failed to save Organization: %s", e)
            messagebox.showerror("Error", f"Failed to save Organization:\n{e}")

    def _handle_create(self):
        self._handle_cancel()

    def _handle_cancel(self):
        self._editing_id = None
        self._form.clear()
        self._save_btn.config(text="Create")
        self._cancel_btn.config(text="Clear")

    def _handle_edit(self, row: dict):
        self._editing_id = row["OrganizationId"]
        self._form.set({
            "name":        row["OrganizationName"],
            "org_type":    row["OrganizationTypeName"],
            "description": row.get("Description"),
        })
        self._save_btn.config(text="Save")
        self._cancel_btn.config(text="Cancel")

    def _handle_delete(self, row: dict):
        org_id = row["OrganizationId"]
        org_name = row["OrganizationName"]
        if not messagebox.askyesno("Confirm Delete", f"Delete organization '{org_name}'?\nThis will also remove it as a Payee."):
            return
        try:
            with get_connection("ldr") as conn:
                conn.execute(text("DELETE FROM [Organization] WHERE OrganizationId=:id"), {"id": org_id})
            if self._editing_id == org_id:
                self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            logger.error("Failed to delete Organization: %s", e)
            messagebox.showerror("Error", f"Failed to delete Organization:\n{e}")


# ──────────────────────────────────────────────────────────────────────────────
# Organization Types tab
# ──────────────────────────────────────────────────────────────────────────────

class _OrganizationTypesTab(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self._editing_id: str | None = None

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Left: form + buttons ──────────────────────────────────
        left = ttk.Frame(self)
        left.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        ttk.Label(left, text="Organization Type", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        self._form = OrganizationTypeForm(left)
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

        self._table = ControlPanelTable(right, title="Organization Types", columns={
            "OrganizationTypeId":   {"is_hidden": True},
            "OrganizationTypeName": {"justify": "left",   "width": 200},
            "IsAccountProvider":    {"justify": "center", "width": 140},
            "Segment":              {"justify": "center", "width": 130},
            "Description":          {"justify": "left",   "width": 280},
        })
        self._table.set_edit_command(self._handle_edit)
        self._table.set_delete_command(self._handle_delete)
        self._table.set_create_command(self._handle_create)
        self._table.grid(row=0, column=0, sticky="nsew")

        self._refresh_table()

    def _refresh_table(self):
        segments = data.InvoiceItemCategory()["Segment"].drop_duplicates().sort_values().tolist()
        cb = self._form.segment_widget
        cb["values"] = segments
        cb._all_values = segments

        df = data.OrganizationTypes()[["OrganizationTypeId", "OrganizationTypeName", "IsAccountProvider", "Segment", "Description"]]
        df = df.copy()
        df["IsAccountProvider"] = df["IsAccountProvider"].map(lambda x: "Yes" if x else "No")
        self._table.data = df.fillna("")

    def _handle_save(self):
        form_data = self._form.get()
        type_name = form_data.get("type_name")
        is_acct_str = form_data.get("is_account_provider")
        segment = form_data.get("segment")
        description = form_data.get("description")

        if not type_name:
            messagebox.showwarning("Validation", "Type Name is required.")
            return
        if is_acct_str not in ("Yes", "No"):
            messagebox.showwarning("Validation", "Is Account Provider must be 'Yes' or 'No'.")
            return
        if not segment:
            messagebox.showwarning("Validation", "Segment is required.")
            return
        if not description:
            messagebox.showwarning("Validation", "Description is required.")
            return

        is_acct = 1 if is_acct_str == "Yes" else 0

        try:
            with get_connection("ldr") as conn:
                if self._editing_id is None:
                    conn.execute(text(
                        "INSERT INTO [OrganizationType] (OrganizationTypeId, OrganizationTypeName, IsAccountProvider, Segment, Description) "
                        "VALUES (:id, :name, :is_acct, :segment, :desc)"
                    ), {"id": str(uuid.uuid4()), "name": type_name, "is_acct": is_acct, "segment": segment, "desc": description})
                else:
                    conn.execute(text(
                        "UPDATE [OrganizationType] SET OrganizationTypeName=:name, IsAccountProvider=:is_acct, Segment=:segment, Description=:desc "
                        "WHERE OrganizationTypeId=:id"
                    ), {"id": self._editing_id, "name": type_name, "is_acct": is_acct, "segment": segment, "desc": description})
            self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            logger.error("Failed to save OrganizationType: %s", e)
            messagebox.showerror("Error", f"Failed to save Organization Type:\n{e}")

    def _handle_create(self):
        self._handle_cancel()

    def _handle_cancel(self):
        self._editing_id = None
        self._form.clear()
        self._save_btn.config(text="Create")
        self._cancel_btn.config(text="Clear")

    def _handle_edit(self, row: dict):
        self._editing_id = row["OrganizationTypeId"]
        self._form.set({
            "type_name":           row["OrganizationTypeName"],
            "is_account_provider": row["IsAccountProvider"],
            "segment":             row["Segment"],
            "description":         row.get("Description"),
        })
        self._save_btn.config(text="Save")
        self._cancel_btn.config(text="Cancel")

    def _handle_delete(self, row: dict):
        type_id = row["OrganizationTypeId"]
        type_name = row["OrganizationTypeName"]
        if not messagebox.askyesno("Confirm Delete", f"Delete organization type '{type_name}'?"):
            return
        try:
            with get_connection("ldr") as conn:
                conn.execute(text("DELETE FROM [OrganizationType] WHERE OrganizationTypeId=:id"), {"id": type_id})
            if self._editing_id == type_id:
                self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            logger.error("Failed to delete OrganizationType: %s", e)
            messagebox.showerror("Error", f"Failed to delete Organization Type.\nIt may be in use by existing organizations.\n\n{e}")
