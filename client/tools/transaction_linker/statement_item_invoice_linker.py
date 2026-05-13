import tkinter as tk
from tkinter import messagebox
from gui import Modal, Table
from .._ui_components import InvoiceSearchForm, StatementItemSearchForm
from color import *
import data
from search import search
from models.Invoice import Invoice, StatementItem
from tools._ui_components import InvoiceCard, StatementItemCard
from db import get_connection


class StatementItemInvoiceReceiptLinker(Modal):

    def __init__(self, app, statement_item:StatementItem, close_callback):
        super().__init__(master=app, background_color=WHITE, border_thickness=2, border_color=BLACK, is_fullscreen=True)
        self._close_callback = close_callback
        self._selected_invoice: Invoice | None = None
        self._selected_statement_item:StatementItem = statement_item
        self._item_row = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Invoice section (left column)
        invoice_section = tk.Frame(self, bg=WHITE)
        invoice_section.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(10, 5), pady=10)
        invoice_section.grid_columnconfigure(0, weight=1)
        invoice_section.grid_rowconfigure(1, weight=1)


        tk.Label(invoice_section, text="Invoice", font=("Segoe UI", 12, "bold"), bg=WHITE, fg=BOLD_BLUE_TEXT).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self._invoice_card_slot = tk.Frame(invoice_section, bg=WHITE, highlightthickness=1, highlightbackground=BLACK)
        self._invoice_card_slot.grid(row=1, column=0, sticky="nsew")
        tk.Button(
            invoice_section, text="Select Invoice", command=self._select_invoice,
            bg=LIGHT_BLUE_BACKGROUND, fg=BLUE_SMALL_TEXT, activebackground=DARK_BLUE_BACKGROUND,
            activeforeground=WHITE, relief="flat", font=("Segoe UI", 10)
        ).grid(row=2, column=0, sticky="ew", pady=(8, 0))




        # Statement items section (right column)
        items_section = tk.Frame(self, bg=WHITE)
        items_section.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(5, 10), pady=10)
        items_section.grid_columnconfigure(0, weight=1)
        items_section.grid_rowconfigure(1, weight=1)

        tk.Label(items_section, text="Statement Items", font=("Segoe UI", 12, "bold"), bg=WHITE, fg=BOLD_BLUE_TEXT).grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        self._statement_items_card_slot = tk.Frame(items_section, bg=WHITE)
        self._statement_items_card_slot.grid(row=1, column=0, sticky="nsew")
        self._statement_items_card_slot.grid_columnconfigure(0, weight=1)
        StatementItemCard(self._statement_items_card_slot, self._selected_statement_item).grid(row=0, column=0, sticky="ew", pady=(0, 4))



        # Link button (full width, bottom)
        tk.Button(
            self, text="Link", command=self._link,
            bg=DARK_BLUE_BACKGROUND, fg=WHITE, activebackground=BLUE_SMALL_TEXT, activeforeground=WHITE,
            relief="flat", font=("Segoe UI", 11, "bold")
        ).grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))


    def _clear_invoice_card_slot(self):
        for child in self._invoice_card_slot.winfo_children():
            child.destroy()


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

        modal = Modal(self, background_color=WHITE)
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

        messagebox.showinfo("Linked", f"Successfully linked statement item to the invoice.")
        self._close_callback()
