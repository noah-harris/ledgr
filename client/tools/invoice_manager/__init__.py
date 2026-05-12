import tkinter as tk
from tkinter import ttk
import pandas as pd
from sqlalchemy import text
from pathlib import Path
from db import get_connection
from functools import cached_property
from gui import Table
from tools import Tool
from config import *
import data

from .edit import InvoiceEditor
from .view import InvoiceViewer

class InvoiceManager(Tool):

    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self._cache_ui_elements()
        self._grid_ui_elements()
        self._bind_controls()

    def _cache_ui_elements(self):
        self.search_frame
        self.search_results_table

    def _grid_ui_elements(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.search_frame.grid        (row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        self.search_results_table.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def _bind_controls(self):
        def _uppercase_payee(*_):
            val = self._payee_var.get()
            upper = val.upper()
            if val != upper:
                self._payee_var.set(upper)

        self._account_var.trace_add("write", lambda *_: self._handle_search())
        self._payee_var.trace_add("write", _uppercase_payee)
        self._payee_var.trace_add("write", lambda *_: self._handle_search())
        self._transaction_date_var.trace_add("write", lambda *_: self._handle_search())
        self._method_var.trace_add("write", lambda *_: self._handle_search())
        self._amount_var.trace_add("write", lambda *_: self._handle_search())
        
        # self.search_results_table.bind("<<TreeviewSelect>>", lambda _: self._handle_select())

    # ==================================================
    # UI ELEMENTS
    # ==================================================

    @cached_property
    def search_frame(self) -> ttk.Frame:
        frame = ttk.Frame(self)

        self._account_var = tk.StringVar()
        self._payee_var = tk.StringVar()
        self._transaction_date_var = tk.StringVar()
        self._method_var = tk.StringVar()
        self._amount_var = tk.StringVar()

        ttk.Label(frame, text="Account:").grid(row=0, column=0, padx=(10, 2), pady=10, sticky="e")
        ttk.Combobox(frame, textvariable=self._account_var, values=[""] + data.Account()["AccountDisplayName"].tolist(), width=40).grid(row=0, column=1, padx=(0, 10), pady=10, sticky="w")

        ttk.Label(frame, text="Method:").grid(row=0, column=6, padx=(10, 2), pady=10, sticky="e")
        self._method_combobox = ttk.Combobox(frame, textvariable=self._method_var, values=[""], width=40)
        self._method_combobox.grid(row=0, column=7, padx=(0, 10), pady=10, sticky="w")

        ttk.Label(frame, text="Payee:").grid(row=0, column=2, padx=(10, 2), pady=10, sticky="e")
        ttk.Combobox(frame, textvariable=self._payee_var, values=[""] + data.Payee()["PayeeName"].tolist(), width=40).grid(row=0, column=3, padx=(0, 10), pady=10, sticky="w")

        ttk.Label(frame, text="Transaction Date:").grid(row=0, column=4, padx=(10, 2), pady=10, sticky="e")
        ttk.Entry(frame, textvariable=self._transaction_date_var, width=14).grid(row=0, column=5, padx=(0, 10), pady=10, sticky="w")

        ttk.Label(frame, text="Amount:").grid(row=0, column=8, padx=(10, 2), pady=10, sticky="e")
        ttk.Entry(frame, textvariable=self._amount_var, width=10).grid(row=0, column=9, padx=(0, 10), pady=10, sticky="w")

        return frame

    @cached_property
    def search_results_table(self) -> Table:
        columns = {
            "Account": {}, "Payee": {}, "TransactionDate": {}, "Method": {}, "Amount": {},
            "Inv": {"width":20}, "Img": {"width":20},
            "StatementItemId": {"is_hidden": True}, "InvoiceId": {"is_hidden": True},
            "ImageId": {"is_hidden": True}, "StatementId": {"is_hidden": True},
            "Edit": {"button": ("Edit", self._handle_edit)},
            "View": {"button": ("View", self._handle_view)},
        }
        table = Table(self, columns=columns)
        table.configure(height=8)
        return table


    # ==================================================
    # HANDLERS
    # ==================================================
    
    def _handle_edit(self, row:dict):
        invoice_id = str(row.get('InvoiceId')).upper()
        InvoiceEditor(self, invoice_id)


    def _handle_view(self, row:dict):
        invoice_id = str(row.get('InvoiceId')).upper()
        InvoiceViewer(self, invoice_id)


    def _handle_search(self):
        #df where invoice_id is not null
        df = data.v_StatementItem()
        df = df[df["InvoiceId"].notna()]
        mask = pd.Series(True, index=df.index)

        account = self._account_var.get()
        payee = self._payee_var.get()
        date = self._transaction_date_var.get().strip()
        method = self._method_var.get()
        amount = self._amount_var.get().strip()

        if account:
            mask &= df["Account"] == account
        if payee:
            mask &= df["Payee"] == payee
        if date:
            mask &= df["TransactionDate"].astype(str).str.contains(date, na=False)
        if method:
            mask &= df["Method"] == method
        if amount:
            mask &= df["Amount"].astype(str).str.contains(amount, na=False)

        results = df[mask].sort_values("TransactionDate", ascending=False)
        self.search_results_table.data = self._with_link_indicators(results)

    # ==================================================
    # HELPERS
    # ==================================================

    def _with_link_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["Inv"] = df["InvoiceId"].apply(lambda v: "✓" if pd.notna(v) and v else "")
        df["Img"] = df["ImageId"].apply(lambda v: "✓" if pd.notna(v) and v else "")
        return df

    def _resolve_image_filename(self, image_id) -> str | None:
        try:
            is_null = not image_id or pd.isna(image_id)
        except (TypeError, ValueError):
            is_null = False
        if is_null or str(image_id).upper() in ("NONE", NO_IMAGE_ID.upper()):
            return None
        with get_connection("ldr") as conn:
            img_df = pd.read_sql_query(
                text("SELECT [ImageFileName] FROM [v_Image] WHERE [ImageId] = :image_id"),
                conn, params={"image_id": image_id}
            )
        if img_df.empty or not img_df["ImageFileName"].iloc[0]:
            return None
        return img_df["ImageFileName"].iloc[0]
