import tkinter as tk
from tkinter import ttk
import pandas as pd
from functools import cached_property

from gui import Table
from tools import Tool
from tools._ui_components import StatementItemSearchForm
from tools.statement_viewer.edit import StatementItemEditor
import data


class StatementItemSearch(Tool):

    def __init__(self, master: tk.Tk):
        super().__init__(master, title="Statement Item Search")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.search_form
        self.search_results

        self.search_form.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        self.search_results.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self._bind_controls()

    @cached_property
    def search_form(self) -> StatementItemSearchForm:
        return StatementItemSearchForm(self)

    @cached_property
    def search_results(self) -> Table:
        columns = {
            "Account": {"justify": "left", "width": 150},
            "StatementDate": {"justify": "center", "width": 100},
            "Payee": {"justify": "left", "width": 150},
            "TransactionDate": {"justify": "center", "width": 100},
            "PostDate": {"justify": "center", "width": 100},
            "Method": {"justify": "left", "width": 180},
            "ReferenceNumber": {"justify": "left", "width": 100},
            "Description": {"justify": "left", "width": 300},
            "Amount": {"justify": "right", "width": 100},
            "StatementItemId": {"is_hidden": True},
            "StatementId": {"is_hidden": True},
            "ImageId": {"is_hidden": True},
            "InvoiceId": {"is_hidden": True},
        }
        return Table(self, columns=columns)

    def _bind_controls(self):
        for widget in (
            self.search_form.account_widget,
            self.search_form.payee_widget,
            self.search_form.method_widget,
        ):
            widget.bind("<KeyRelease>", lambda e: self._handle_search(), add="+")
            widget.bind("<<ComboboxSelected>>", lambda e: self._handle_search(), add="+")

        self.search_form.transaction_date_widget.bind("<KeyRelease>", lambda e: self._handle_search(), add="+")
        self.search_form.transaction_date_time_widget.bind("<KeyRelease>", lambda e: self._handle_search(), add="+")
        self.search_form.amount_widget.bind("<KeyRelease>", lambda e: self._handle_search(), add="+")

        self.search_results.bind("<Double-1>", lambda e: self._handle_double_click())

    def _handle_search(self):
        state = self.search_form.get()

        df = data.v_StatementItem()
        mask = pd.Series(True, index=df.index)
        any_filter = False

        if state.get("account"):
            mask &= df["Account"] == state["account"]
            any_filter = True
        if state.get("payee"):
            mask &= df["Payee"] == state["payee"]
            any_filter = True
        if state.get("method"):
            mask &= df["Method"] == state["method"]
            any_filter = True
        if state.get("transaction_date"):
            mask &= df["TransactionDate"].astype(str).str.contains(str(state["transaction_date"]), na=False)
            any_filter = True
        if state.get("amount"):
            mask &= df["Amount"].astype(str).str.contains(str(state["amount"]), na=False)
            any_filter = True

        if not any_filter:
            self.search_results.data = pd.DataFrame()
            return

        results = df[mask].sort_values("TransactionDate", ascending=False)
        self.search_results.data = results

    def _handle_double_click(self):
        row = self.search_results.get_selected_row()
        if not row:
            return
        statement_item_id = row.get("StatementItemId")
        if not statement_item_id:
            return

        account_id = None
        account_name = row.get("Account")
        if account_name:
            accounts = data.Account()
            match = accounts[accounts["AccountDisplayName"] == account_name]
            if not match.empty:
                account_id = str(match.iloc[0]["AccountId"]).upper()

        StatementItemEditor(
            self,
            statement_item_id=str(statement_item_id).upper(),
            account_id=account_id,
            on_save=self._handle_search,
        )
