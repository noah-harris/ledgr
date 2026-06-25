import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from gui import Modal, Table
from .._ui_components import InvoiceSearchForm, StatementItemSearchForm
from style import CARD, PRIMARY_DARKER, BORDER_STRONG, FONT
import data
from search import search
from models.Invoice import Invoice, StatementItem
from tools._ui_components import InvoiceCard, StatementItemCard
from db import get_connection


class StatementItemInvoiceReceiptLinker(Modal):

    def __init__(self, app, statement_item:StatementItem, queue_df:pd.DataFrame, close_callback):
        super().__init__(master=app, background_color=CARD, border_thickness=2, border_color=BORDER_STRONG, is_fullscreen=True)
        self._close_callback = close_callback
        self._selected_invoice: Invoice | None = None
        self._selected_statement_item:StatementItem = statement_item
        self._queue_df = queue_df.copy()
        self._syncing_table = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Invoice section (left column)
        invoice_section = ttk.Frame(self, style='Card.TFrame')
        invoice_section.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(10, 5), pady=10)
        invoice_section.grid_columnconfigure(0, weight=1)
        invoice_section.grid_rowconfigure(1, weight=1)

        ttk.Label(invoice_section, text="Invoice", font=(FONT, 12, 'bold'), foreground=PRIMARY_DARKER, style='Card.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 4))
        self._invoice_card_slot = ttk.Frame(invoice_section, style='Bordered.Card.TFrame')
        self._invoice_card_slot.grid(row=1, column=0, sticky="nsew")
        ttk.Button(
            invoice_section, text="Select Invoice", command=self._select_invoice,
        ).grid(row=2, column=0, sticky="ew", pady=(8, 0))

        # Statement items section (center column)
        items_section = ttk.Frame(self, style='Card.TFrame')
        items_section.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=10)
        items_section.grid_columnconfigure(0, weight=1)
        items_section.grid_rowconfigure(1, weight=1)

        ttk.Label(items_section, text="Statement Items", font=(FONT, 12, 'bold'), foreground=PRIMARY_DARKER, style='Card.TLabel').grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        self._statement_items_card_slot = ttk.Frame(items_section, style='Card.TFrame')
        self._statement_items_card_slot.grid(row=1, column=0, sticky="nsew")
        self._statement_items_card_slot.grid_columnconfigure(0, weight=1)
        StatementItemCard(self._statement_items_card_slot, self._selected_statement_item).grid(row=0, column=0, sticky="ew", pady=(0, 4))

        # Queue section (right column)
        queue_section = ttk.Frame(self, style='Card.TFrame')
        queue_section.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(5, 10), pady=10)
        queue_section.grid_columnconfigure(0, weight=1)
        queue_section.grid_rowconfigure(1, weight=1)

        header = ttk.Frame(queue_section, style='Card.TFrame')
        header.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Queue", font=(FONT, 12, 'bold'), foreground=PRIMARY_DARKER, style='Card.TLabel').grid(row=0, column=0, sticky="w")
        self._queue_count_var = tk.StringVar()
        ttk.Label(header, textvariable=self._queue_count_var, style='Card.TLabel').grid(row=0, column=1, sticky="e")

        self._queue_table = Table(queue_section, columns={
            "StatementItemId": {"is_hidden": True},
            "Payee": {"justify": "left", "width": 150},
            "TransactionDate": {"justify": "center", "width": 100},
            "Amount": {"justify": "right", "width": 80},
            "Account": {"justify": "left", "width": 120},
        })
        self._queue_table.grid(row=1, column=0, sticky="nsew")
        self._queue_table.bind("<<TreeviewSelect>>", self._handle_queue_table_select)

        self._refresh_queue_table()
        self._sync_table_to_queue()

        # Link button (full width, bottom)
        ttk.Button(
            self, text="Link", command=self._link, style='Accent.TButton',
        ).grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))


    def _clear_invoice_card_slot(self):
        for child in self._invoice_card_slot.winfo_children():
            child.destroy()

    def _refresh_statement_item_card(self):
        for child in self._statement_items_card_slot.winfo_children():
            child.destroy()
        StatementItemCard(self._statement_items_card_slot, self._selected_statement_item).grid(
            row=0, column=0, sticky="ew", pady=(0, 4)
        )

    # ── Queue helpers ─────────────────────────────────────────

    def _refresh_queue_table(self):
        display_df = self._queue_df[["StatementItemId", "Payee", "TransactionDate", "Amount", "Account"]].copy()
        self._queue_table.data = display_df
        self._queue_count_var.set(f"{len(display_df)} remaining")

    def _sync_table_to_queue(self):
        self._syncing_table = True
        try:
            current_id = str(self._selected_statement_item.StatementItemId)
            for item_id in self._queue_table.get_children():
                vals = self._queue_table.item(item_id)["values"]
                if str(vals[0]).upper() == current_id.upper():
                    self._queue_table.selection_set(item_id)
                    self._queue_table.see(item_id)
                    break
        finally:
            self._syncing_table = False

    def _handle_queue_table_select(self, event=None):
        if self._syncing_table:
            return
        row = self._queue_table.get_selected_row()
        if row is None:
            return
        selected_id = row["StatementItemId"]
        if str(selected_id) == str(self._selected_statement_item.StatementItemId):
            return
        self._selected_statement_item = StatementItem(selected_id)
        self._refresh_statement_item_card()
        self._selected_invoice = None
        self._clear_invoice_card_slot()

    # ── Invoice search ────────────────────────────────────────

    def v_Invoice(self):
        df = data.v_Invoice()
        df = df[df["PayeeName"] == self._selected_statement_item.PayeeName]
        return df

    def _select_invoice(self):

        def _on_search_change(_):
            state = invoice_search_form.get()

            matches = search(
                df=self.v_Invoice(),
                fields={
                    "PayeeName": {"value": state["payee"]},
                    "InvoiceDate": {"value": state["invoice_date"]},
                    "DueDate": {"value": state["due_date"]},
                    "InvoiceNumber": {"value": state["invoice_number"]},
                    "Amount": {"value": state["amount"]}
                }
            )
            invoice_search_results.data = matches

        def _on_select():
            row = invoice_search_results.get_selected_row()
            if row:
                invoice = Invoice(row["InvoiceId"])
                self._selected_invoice = invoice
                self._clear_invoice_card_slot()
                InvoiceCard(self._invoice_card_slot, invoice, show_receipts=False).pack(fill="both", expand=True)
            modal.close()

        modal = Modal(self, background_color=CARD)
        invoice_search_form = InvoiceSearchForm(modal)
        invoice_search_results = Table(modal, columns={
            "InvoiceId": {"is_hidden": True},
            "PayeeId": {"is_hidden": True},
            "PayeeName": {"justify": "left", "width": 150},
            "InvoiceDate": {"justify": "center", "width": 100},
            "DueDate": {"justify": "center", "width": 100},
            "InvoiceNumber": {"justify": "left", "width": 100},
            "Amount": {"justify": "left", "width": 100},
            "Description": {"justify": "left", "width": 400},
            "StartDate": {"justify": "center", "width": 100},
            "EndDate": {"justify": "center", "width": 100},
            "ImageId": {"is_hidden": True}
        }, visible_rows=20)
        invoice_search_results.data = self.v_Invoice()

        invoice_search_form.payee_widget.bind("<KeyRelease>", _on_search_change, add="+")
        invoice_search_form.invoice_date_widget.bind("<KeyRelease>", _on_search_change, add="+")
        invoice_search_form.invoice_date_time_widget.bind("<KeyRelease>", _on_search_change, add="+")
        invoice_search_form.due_date_widget.bind("<KeyRelease>", _on_search_change, add="+")
        invoice_search_form.invoice_number_widget.bind("<KeyRelease>", _on_search_change, add="+")
        invoice_search_form.payee_widget.bind("<<ComboboxSelected>>", _on_search_change, add="+")
        invoice_search_results.bind("<Double-1>", lambda e: _on_select())

        invoice_search_form.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        invoice_search_results.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))


    def _link(self):
        if self._selected_invoice is None:
            messagebox.showwarning("No Invoice", "Please select an invoice before linking.")
            return
        if not self._selected_statement_item:
            messagebox.showwarning("No Items", "Please add at least one statement item before linking.")
            return

        invoice = self._selected_invoice
        item = self._selected_statement_item

        msg = f"Invoice: {invoice.PayeeName} · {invoice.InvoiceDate.strftime('%m/%d/%Y')} · ${invoice.Amount}\n\n"
        msg += f"Statement Item:\n"
        msg += f"  · {item.AccountOrganizationName} {item.PaymentDisplayNumber} · ${item.Amount} · {item.TransactionDate}\n"
        msg += "\nLink these statement items to the invoice?"

        if not messagebox.askyesno("Confirm Link", msg):
            return

        with get_connection("ldr") as conn:
            data.update_statement_item_invoice_id(conn, invoice.InvoiceId, item.StatementItemId)

        messagebox.showinfo("Linked", "Successfully linked statement item to the invoice.")

        self._queue_df = self._queue_df[
            self._queue_df["StatementItemId"].astype(str) != str(item.StatementItemId)
        ]

        if self._queue_df.empty:
            self._close_callback()
            return

        next_id = self._queue_df.iloc[0]["StatementItemId"]
        self._selected_statement_item = StatementItem(next_id)
        self._selected_invoice = None
        self._clear_invoice_card_slot()
        self._refresh_statement_item_card()
        self._refresh_queue_table()
        self._sync_table_to_queue()
