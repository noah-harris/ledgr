import tkinter as tk
from tkinter import ttk
import pandas as pd
from sqlalchemy import text
from db import get_connection
from functools import cached_property
from gui import Table, ImageViewer
from tools import Tool
from config import *
from resolve_image_bytes import resolve_image_bytes
from pathlib import Path

class StatementViewer(Tool):

    def __init__(self, master: tk.Tk):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=0)  # combobox header
        self.grid_rowconfigure(1, weight=0)  # statement table (fixed, 1 row)
        self.grid_rowconfigure(2, weight=1)  # statement item table (expands)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        self._statement_text_variable = tk.StringVar()
        self._account_text_variable = tk.StringVar()

        # Force widget creation
        self.combobox_frame
        self.account_combobox
        self.statement_combobox
        self.statement_item_table
        self.statement_table
        self.image_viewer

        self.account_combobox.bind("<<ComboboxSelected>>", self._handle_account_selection)
        self.statement_combobox.bind("<<ComboboxSelected>>", self._handle_statement_selection)

    # ──────────────────────────────────────────────────────────
    # EVENT HANDLERS
    # ──────────────────────────────────────────────────────────

    def _handle_account_selection(self, event):
        # Reset the statement selection
        self._statement_text_variable.set("")

        account_name = self._account_text_variable.get()
        statements_for_account = self.statement_options.get(account_name, {})

        # Statements are already sorted by StatementDate desc in statement_options,
        # so dict insertion order preserves that ordering.
        self.statement_combobox.configure(values=list(statements_for_account.keys()))

        # Clear downstream widgets until a statement is picked
        empty_df = pd.DataFrame()
        self.statement_table.data = empty_df
        self.statement_item_table.data = empty_df
        self.image_viewer.path = None

    def _handle_statement_selection(self, event):
        if self.account_id is None or self.statement_id is None:
            return
        self.statement_table.data = self.statement_data
        self.statement_item_table.data = self.statement_item_data
        filename = self.image_path
        if filename:
            # img_bytes = fetch_image_bytes(filename)
            img_bytes = resolve_image_bytes(f"{IMAGE_DIRECTORY}/{filename}")
            if img_bytes:
                self.image_viewer.load_from_bytes(img_bytes, Path(filename).suffix.lstrip("."), Path(filename).stem)
            else:
                self.image_viewer.show_placeholder("Image unavailable")

    # ──────────────────────────────────────────────────────────
    # WIDGETS
    # ──────────────────────────────────────────────────────────

    @cached_property
    def image_viewer(self):
        img = ImageViewer(self)
        img.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=10, pady=10)
        return img

    @cached_property
    def combobox_frame(self):
        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        # Two label+combobox pairs side by side; let the comboboxes take the slack
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=0)
        frame.grid_columnconfigure(3, weight=1)
        return frame

    @cached_property
    def account_combobox(self):
        values = list(self.account_options.keys())
        ttk.Label(self.combobox_frame, text="Account:").grid(
            row=0, column=0, padx=(0, 5), sticky="w"
        )
        account_cb = ttk.Combobox(
            self.combobox_frame,
            values=values,
            textvariable=self._account_text_variable,
            state="readonly",
        )
        account_cb.grid(row=0, column=1, padx=(0, 15), sticky="ew")
        account_cb.configure(width=30)
        return account_cb

    @cached_property
    def statement_combobox(self):
        ttk.Label(self.combobox_frame, text="Statement:").grid(
            row=0, column=2, padx=(0, 5), sticky="w"
        )
        statement_cb = ttk.Combobox(
            self.combobox_frame,
            values=[],
            textvariable=self._statement_text_variable,
            state="readonly",
        )
        statement_cb.grid(row=0, column=3, sticky="ew")
        statement_cb.configure(width=30)
        return statement_cb

    @cached_property
    def statement_table(self):
        columns = {
            "Account": {}, "Statement Date": {}, "Start Date": {}, "End Date": {},
            "Statement Period": {}, "Start Balance": {}, "End Balance": {}, "Balance Change": {},
        }
        statement_table = Table(self, columns=columns)
        statement_table.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        statement_table.configure(height=1)
        return statement_table

    @cached_property
    def statement_item_table(self):
        columns = {
            "Payee": {}, "Method": {}, "Transaction Date": {}, "Post Date": {},
            "Reference Number": {}, "Description": {}, "Amount": {},
        }
        statement_item_table = Table(self, columns=columns)
        statement_item_table.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        statement_item_table.configure(height=50)
        return statement_item_table

    # ──────────────────────────────────────────────────────────
    # DATA
    # ──────────────────────────────────────────────────────────

    @cached_property
    def account_options(self):
        with get_connection("ldr") as conn:
            data = pd.read_sql_query(
                text("SELECT [AccountId], [AccountDisplayName] FROM [v_Account] ORDER BY [AccountDisplayName]"),
                conn,
            )
        return dict(zip(data["AccountDisplayName"], data["AccountId"]))

    @cached_property
    def statement_options(self):
        with get_connection("ldr") as conn:
            data = pd.read_sql_query(
                text("""
                    SELECT
                        [AccountDisplayName],
                        [StatementDate],
                        [AccountId],
                        [StatementId],
                        [StatementDisplayName]
                    FROM [v_Statement]
                    ORDER BY [AccountDisplayName], [StatementDate] DESC
                """),
                conn,
            )

        # {AccountDisplayName: {StatementDisplayName: {StatementFields}}}
        # Rows come back pre-sorted by StatementDate DESC per account,
        # so dict insertion order reflects that.
        statement_dict: dict = {}
        for _, row in data.iterrows():
            account_name = row["AccountDisplayName"]
            statement_name = row["StatementDisplayName"]
            statement_dict.setdefault(account_name, {})[statement_name] = {
                "AccountId": row["AccountId"],
                "StatementId": row["StatementId"],
                "StatementDate": row["StatementDate"],
            }
        return statement_dict

    @property
    def account_id(self):
        return self.account_options.get(self._account_text_variable.get())

    @property
    def statement_id(self):
        account_name = self._account_text_variable.get()
        statement_name = self._statement_text_variable.get()
        entry = self.statement_options.get(account_name, {}).get(statement_name)
        if entry is None:
            return None
        return entry["StatementId"]

    @property
    def statement_data(self):
        with get_connection("ldr") as conn:
            data = pd.read_sql_query(
                text("""
                    SELECT
                        [AccountId],
                        [AccountDisplayName] AS [Account],
                        [StatementId],
                        [StatementDisplayName],
                        [StatementDate] AS [Statement Date],
                        [StartDate] AS [Start Date],
                        [EndDate] AS [End Date],
                        [StatementPeriod] AS [Statement Period],
                        [StartBalance] AS [Start Balance],
                        [EndBalance] AS [End Balance],
                        [BalanceChange] AS [Balance Change],
                        [ImageFileName]
                    FROM [v_Statement]
                    WHERE [StatementId] = :statement_id
                """),
                conn,
                params={"statement_id": self.statement_id},
            )
        return data

    @property
    def statement_item_data(self):
        with get_connection("ldr") as conn:
            data = pd.read_sql_query(
                text("""
                    SELECT
                        [AccountDisplayName] AS [Account],
                        [StatementDate] AS [Statement Date],
                        [PayeeName] AS [Payee],
                        [MethodDisplayName] AS [Method],
                        [TransactionDate] AS [Transaction Date],
                        [PostDate] AS [Post Date],
                        [ReferenceNumber] AS [Reference Number],
                        [Description] AS [Description],
                        [Amount] AS [Amount]
                    FROM [v_StatementItem]
                    WHERE [StatementId] = :statement_id
                    ORDER BY [PostDate] DESC, [TransactionDate] DESC
                """),
                conn,
                params={"statement_id": self.statement_id},
            )
        return data

    @property
    def image_path(self) -> str | None:
        df = self.statement_data
        if df.empty:
            return None
        val = df["ImageFileName"].iloc[0]
        return val if val else None