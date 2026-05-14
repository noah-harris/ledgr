import uuid
from tkinter import messagebox, ttk
import tkinter as tk

from sqlalchemy import text

import data
from config import make_logger
from db import get_connection
from gui import ControlPanelTable
from tools import Tool
from .._ui_components.account_form import AccountForm
from .._ui_components.account_type_form import AccountTypeForm

logger = make_logger(__name__)


class AccountCreator(Tool):

    def __init__(self, master: tk.Tk):
        super().__init__(master, title="Account Manager")
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        accounts_tab = _AccountsTab(notebook)
        types_tab = _AccountTypesTab(notebook)
        notebook.add(accounts_tab, text="Accounts")
        notebook.add(types_tab, text="Account Types")

        def _on_tab_change(_event):
            idx = notebook.index(notebook.select())
            if idx == 0:
                accounts_tab._refresh_table()
            else:
                types_tab._refresh_table()

        notebook.bind("<<NotebookTabChanged>>", _on_tab_change)


# ──────────────────────────────────────────────────────────────────────────────
# Accounts tab
# ──────────────────────────────────────────────────────────────────────────────

class _AccountsTab(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self._editing_id: str | None = None

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Left: form + buttons ──────────────────────────────────
        left = ttk.Frame(self)
        left.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        ttk.Label(left, text="Account", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        self._form = AccountForm(left)
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

        self._table = ControlPanelTable(right, title="Accounts", columns={
            "AccountId":          {"is_hidden": True},
            "UsersId":            {"is_hidden": True},
            "AccountTypeId":      {"is_hidden": True},
            "OrganizationId":     {"is_hidden": True},
            "AccountNumber":      {"is_hidden": True},
            "AccountTypeName":    {"is_hidden": True},
            "OrganizationName":   {"is_hidden": True},
            "FirstName":          {"is_hidden": True},
            "LastName":           {"is_hidden": True},
            "AccountDisplayName": {"justify": "left",   "width": 260},
            "Username":           {"justify": "left",   "width": 120},
            "Currency":           {"justify": "center", "width":  70},
            "StartDate":          {"justify": "center", "width": 110},
            "EndDate":            {"justify": "center", "width": 110},
            "Description":        {"justify": "left",   "width": 200},
        })
        self._table.set_edit_command(self._handle_edit)
        self._table.set_delete_command(self._handle_delete)
        self._table.set_create_command(self._handle_create)
        self._table.grid(row=0, column=0, sticky="nsew")

        self._refresh_table()

    def _refresh_table(self):
        users = data.Users()["FullName"].tolist()
        self._form.users_widget["values"] = users
        self._form.users_widget._all_values = users

        orgs = data.BankOrganization()["OrganizationName"].tolist()
        self._form.organization_widget["values"] = orgs
        self._form.organization_widget._all_values = orgs

        types = data.AccountType()["AccountTypeName"].tolist()
        self._form.account_type_widget["values"] = types
        self._form.account_type_widget._all_values = types

        currencies = data.Currency()["Currency"].tolist()
        self._form.currency_widget["values"] = currencies
        self._form.currency_widget._all_values = currencies

        cols = [
            "AccountId", "UsersId", "AccountTypeId", "OrganizationId",
            "AccountNumber", "AccountTypeName", "OrganizationName", "FirstName", "LastName",
            "AccountDisplayName", "Username", "Currency", "StartDate", "EndDate", "Description",
        ]
        df = data.Account()[cols]
        self._table.data = df.fillna("")

    def _handle_save(self):
        form_data = self._form.get()
        full_name    = form_data.get("users", "").strip()
        org_name     = form_data.get("organization", "").strip()
        type_name    = form_data.get("account_type", "").strip()
        account_num  = form_data.get("account_number", "").strip()
        currency     = form_data.get("currency", "").strip()
        start_date   = form_data.get("start_date", "").strip()
        end_date     = form_data.get("end_date", "").strip()
        description  = form_data.get("description", "").strip() or None

        if not full_name:
            messagebox.showwarning("Validation", "User is required.")
            return
        if not org_name:
            messagebox.showwarning("Validation", "Organization is required.")
            return
        if not type_name:
            messagebox.showwarning("Validation", "Account Type is required.")
            return
        if not account_num:
            messagebox.showwarning("Validation", "Account Number is required.")
            return
        if not currency:
            messagebox.showwarning("Validation", "Currency is required.")
            return

        users_df = data.Users()
        users_match = users_df[users_df["FullName"] == full_name]
        if users_match.empty:
            messagebox.showwarning("Validation", f"Unknown user: '{full_name}'")
            return
        users_id = str(users_match.iloc[0]["UsersId"])

        orgs_df = data.BankOrganization()
        org_match = orgs_df[orgs_df["OrganizationName"] == org_name]
        if org_match.empty:
            messagebox.showwarning("Validation", f"Unknown organization: '{org_name}'")
            return
        org_id = str(org_match.iloc[0]["OrganizationId"])

        types_df = data.AccountType()
        type_match = types_df[types_df["AccountTypeName"] == type_name]
        if type_match.empty:
            messagebox.showwarning("Validation", f"Unknown account type: '{type_name}'")
            return
        type_id = str(type_match.iloc[0]["AccountTypeId"])

        try:
            with get_connection("ldr") as conn:
                if self._editing_id is None:
                    conn.execute(text(
                        "INSERT INTO [Account] "
                        "(AccountId, UsersId, AccountTypeId, OrganizationId, "
                        "AccountNumber, Currency, Description, StartDate, EndDate) "
                        "VALUES (:id, :users_id, :type_id, :org_id, "
                        ":num, :cur, :desc, :start, :end)"
                    ), {
                        "id": str(uuid.uuid4()), "users_id": users_id,
                        "type_id": type_id, "org_id": org_id,
                        "num": account_num, "cur": currency,
                        "desc": description, "start": start_date, "end": end_date,
                    })
                else:
                    conn.execute(text(
                        "UPDATE [Account] SET "
                        "UsersId=:users_id, AccountTypeId=:type_id, OrganizationId=:org_id, "
                        "AccountNumber=:num, Currency=:cur, Description=:desc, "
                        "StartDate=:start, EndDate=:end "
                        "WHERE AccountId=:id"
                    ), {
                        "id": self._editing_id, "users_id": users_id,
                        "type_id": type_id, "org_id": org_id,
                        "num": account_num, "cur": currency,
                        "desc": description, "start": start_date, "end": end_date,
                    })
            self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            logger.error("Failed to save Account: %s", e)
            messagebox.showerror("Error", f"Failed to save Account:\n{e}")

    def _handle_create(self):
        self._handle_cancel()

    def _handle_cancel(self):
        self._editing_id = None
        self._form.clear()
        self._save_btn.config(text="Create")
        self._cancel_btn.config(text="Clear")

    def _handle_edit(self, row: dict):
        self._editing_id = row["AccountId"]
        full_name = f"{row['FirstName']} {row['LastName']}"
        self._form.set({
            "users":          full_name,
            "organization":   row["OrganizationName"],
            "account_type":   row["AccountTypeName"],
            "account_number": row["AccountNumber"],
            "currency":       row["Currency"],
            "start_date":     row["StartDate"],
            "end_date":       row["EndDate"],
            "description":    row.get("Description"),
        })
        self._save_btn.config(text="Save")
        self._cancel_btn.config(text="Cancel")

    def _handle_delete(self, row: dict):
        account_id = row["AccountId"]
        display = row["AccountDisplayName"]
        if not messagebox.askyesno("Confirm Delete", f"Delete account '{display}'?"):
            return
        try:
            with get_connection("ldr") as conn:
                conn.execute(text("DELETE FROM [Account] WHERE AccountId=:id"), {"id": account_id})
            if self._editing_id == account_id:
                self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            logger.error("Failed to delete Account: %s", e)
            messagebox.showerror("Error", f"Failed to delete Account.\nIt may be referenced by other records.\n\n{e}")


# ──────────────────────────────────────────────────────────────────────────────
# Account Types tab
# ──────────────────────────────────────────────────────────────────────────────

class _AccountTypesTab(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self._editing_id: str | None = None

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Left: form + buttons ──────────────────────────────────
        left = ttk.Frame(self)
        left.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        ttk.Label(left, text="Account Type", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        self._form = AccountTypeForm(left)
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

        self._table = ControlPanelTable(right, title="Account Types", columns={
            "AccountTypeId":   {"is_hidden": True},
            "AccountTypeName": {"justify": "left",   "width": 200},
            "IsCredit":        {"justify": "center", "width":  80},
            "Description":     {"justify": "left",   "width": 280},
        })
        self._table.set_edit_command(self._handle_edit)
        self._table.set_delete_command(self._handle_delete)
        self._table.set_create_command(self._handle_create)
        self._table.grid(row=0, column=0, sticky="nsew")

        self._refresh_table()

    def _refresh_table(self):
        df = data.AccountType()[["AccountTypeId", "AccountTypeName", "IsCredit", "Description"]]
        df = df.copy()
        df["IsCredit"] = df["IsCredit"].map(lambda x: "Yes" if x else "No")
        self._table.data = df.fillna("")

    def _handle_save(self):
        form_data   = self._form.get()
        type_name   = form_data.get("type_name", "").strip()
        is_credit_s = form_data.get("is_credit", "").strip()
        description = form_data.get("description", "").strip() or None

        if not type_name:
            messagebox.showwarning("Validation", "Type Name is required.")
            return
        if is_credit_s not in ("Yes", "No"):
            messagebox.showwarning("Validation", "Is Credit must be 'Yes' or 'No'.")
            return

        is_credit = 1 if is_credit_s == "Yes" else 0

        try:
            with get_connection("ldr") as conn:
                if self._editing_id is None:
                    conn.execute(text(
                        "INSERT INTO [AccountType] (AccountTypeId, AccountTypeName, IsCredit, Description) "
                        "VALUES (:id, :name, :is_credit, :desc)"
                    ), {"id": str(uuid.uuid4()), "name": type_name, "is_credit": is_credit, "desc": description})
                else:
                    conn.execute(text(
                        "UPDATE [AccountType] SET AccountTypeName=:name, IsCredit=:is_credit, Description=:desc "
                        "WHERE AccountTypeId=:id"
                    ), {"id": self._editing_id, "name": type_name, "is_credit": is_credit, "desc": description})
            self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            logger.error("Failed to save AccountType: %s", e)
            messagebox.showerror("Error", f"Failed to save Account Type:\n{e}")

    def _handle_create(self):
        self._handle_cancel()

    def _handle_cancel(self):
        self._editing_id = None
        self._form.clear()
        self._save_btn.config(text="Create")
        self._cancel_btn.config(text="Clear")

    def _handle_edit(self, row: dict):
        self._editing_id = row["AccountTypeId"]
        self._form.set({
            "type_name":   row["AccountTypeName"],
            "is_credit":   row["IsCredit"],
            "description": row.get("Description"),
        })
        self._save_btn.config(text="Save")
        self._cancel_btn.config(text="Cancel")

    def _handle_delete(self, row: dict):
        type_id   = row["AccountTypeId"]
        type_name = row["AccountTypeName"]
        if not messagebox.askyesno("Confirm Delete", f"Delete account type '{type_name}'?"):
            return
        try:
            with get_connection("ldr") as conn:
                conn.execute(text("DELETE FROM [AccountType] WHERE AccountTypeId=:id"), {"id": type_id})
            if self._editing_id == type_id:
                self._handle_cancel()
            self._refresh_table()
        except Exception as e:
            logger.error("Failed to delete AccountType: %s", e)
            messagebox.showerror("Error", f"Failed to delete Account Type.\nIt may be in use by existing accounts.\n\n{e}")
