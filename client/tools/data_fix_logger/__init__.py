import uuid
from tkinter import messagebox, ttk
import tkinter as tk

from sqlalchemy import text

import data
from db import get_connection
from gui import ControlPanelTable
from tools import Tool


class DataFixLogger(Tool):

    def __init__(self, master: tk.Tk):
        super().__init__(master, title="Data Fix Log")

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._editing_id: str | None = None

        # ── Left: form + buttons ──────────────────────────────────
        left = ttk.Frame(self)
        left.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        ttk.Label(left, text="Data Fix", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        form = ttk.Frame(left)
        form.pack(padx=10, pady=10)

        ttk.Label(form, text="Description:").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self._desc_entry = ttk.Entry(form, width=50)
        self._desc_entry.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="Statement:").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self._stmt_text = tk.Text(form, width=50, height=10, wrap="word")
        self._stmt_text.grid(row=3, column=0, sticky="ew", pady=(0, 8))

        self._is_updated_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(form, text="Is Updated", variable=self._is_updated_var).grid(
            row=4, column=0, sticky="w", pady=(0, 8)
        )

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

        self._table = ControlPanelTable(right, title="Data Fixes", columns={
            "DataFixId":          {"is_hidden": True},
            "DataFixDescription": {"justify": "left", "width": 300},
            "Statement":          {"justify": "left", "width": 300},
            "IsUpdated":          {"justify": "center", "width": 80},
        })
        self._table.set_edit_command(self._handle_edit)
        self._table.set_delete_command(self._handle_delete)
        self._table.set_create_command(self._handle_create)
        self._table.grid(row=0, column=0, sticky="nsew")

        self._refresh_table()

    # ──────────────────────────────────────────────────────────
    # Data
    # ──────────────────────────────────────────────────────────

    def _refresh_table(self):
        df = data.DataFix()[["DataFixId", "DataFixDescription", "Statement", "IsUpdated"]]
        df = df.copy()
        df["IsUpdated"] = df["IsUpdated"].map(lambda x: "Yes" if x else "No")
        self._table.data = df.fillna("")

    # ──────────────────────────────────────────────────────────
    # Form helpers
    # ──────────────────────────────────────────────────────────

    def _get_form_data(self) -> dict:
        return {
            "description": self._desc_entry.get().strip(),
            "statement": self._stmt_text.get("1.0", "end-1c").strip() or None,
            "is_updated": self._is_updated_var.get(),
        }

    def _set_form_data(self, row: dict):
        self._desc_entry.delete(0, "end")
        self._desc_entry.insert(0, row.get("DataFixDescription", ""))

        self._stmt_text.delete("1.0", "end")
        stmt = row.get("Statement", "")
        if stmt:
            self._stmt_text.insert("1.0", stmt)

        self._is_updated_var.set(row.get("IsUpdated", "") == "Yes")

    def _clear_form(self):
        self._desc_entry.delete(0, "end")
        self._stmt_text.delete("1.0", "end")
        self._is_updated_var.set(False)

    # ──────────────────────────────────────────────────────────
    # Handlers
    # ──────────────────────────────────────────────────────────

    def _handle_save(self):
        form = self._get_form_data()

        if not form["description"]:
            messagebox.showwarning("Validation", "Description is required.")
            return

        is_updated = 1 if form["is_updated"] else 0

        try:
            with get_connection("ldr") as conn:
                if self._editing_id is None:
                    conn.execute(text(
                        "INSERT INTO [DataFix] (DataFixId, DataFixDescription, [Statement], IsUpdated) "
                        "VALUES (:id, :desc, :stmt, :updated)"
                    ), {
                        "id": str(uuid.uuid4()),
                        "desc": form["description"],
                        "stmt": form["statement"],
                        "updated": is_updated,
                    })
                else:
                    conn.execute(text(
                        "UPDATE [DataFix] SET DataFixDescription=:desc, [Statement]=:stmt, IsUpdated=:updated "
                        "WHERE DataFixId=:id"
                    ), {
                        "id": self._editing_id,
                        "desc": form["description"],
                        "stmt": form["statement"],
                        "updated": is_updated,
                    })
            self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data fix:\n{e}")

    def _handle_create(self):
        self._handle_cancel()

    def _handle_cancel(self):
        self._editing_id = None
        self._clear_form()
        self._save_btn.config(text="Create")
        self._cancel_btn.config(text="Clear")

    def _handle_edit(self, row: dict):
        self._editing_id = row["DataFixId"]
        self._set_form_data(row)
        self._save_btn.config(text="Save")
        self._cancel_btn.config(text="Cancel")

    def _handle_delete(self, row: dict):
        data_fix_id = row["DataFixId"]
        desc = row["DataFixDescription"]
        if not messagebox.askyesno("Confirm Delete", f"Delete data fix '{desc}'?"):
            return
        try:
            with get_connection("ldr") as conn:
                conn.execute(text("DELETE FROM [DataFix] WHERE DataFixId=:id"), {"id": data_fix_id})
            if self._editing_id == data_fix_id:
                self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete data fix:\n{e}")
