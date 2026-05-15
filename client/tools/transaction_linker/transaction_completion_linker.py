import tkinter as tk
from tkinter import ttk, messagebox
from gui import Modal, ImageQueue
from .._ui_components import InvoiceForm, InvoiceItemTable
from functools import cached_property
import re
from decimal import Decimal
from db import get_connection
from sqlalchemy import text, engine
import pandas as pd
import data
from style import CARD, BORDER_STRONG, FONT, SUCCESS, DANGER
import uuid

from models.Invoice import StatementItem
from .._ui_components import StatementItemCard

class TransactionCompletionLinker(Modal):

    def __init__(self, master, statement_item:StatementItem, close_callback):
        super().__init__(master, background_color=CARD, border_thickness=2, border_color=BORDER_STRONG)
        self._close_callback = close_callback
        self.invoice_form:InvoiceForm = InvoiceForm(self)
        self.statement_item:StatementItem = statement_item

        StatementItemCard(self, self.statement_item).grid(row=0, column=0)
        self.invoice_form.payee = self.statement_item.PayeeName
        self.invoice_form.amount = self.statement_item.Amount[1:]

        def _grid_ui_elements():
            self.header.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
            self.invoice_form.grid(row=2, column=0, rowspan=1, columnspan=1, padx=10, pady=(0,10), sticky="w")
            self.invoice_item_table.grid(row=2, column=1, columnspan=2, padx=(0,10), sticky="nsew")
            ttk.Button(self, text="Save", command=lambda: self._save()).grid(row=3, column=0, padx=10, pady=10, sticky="w")
            self.invoice_item_table_controls.grid(row=3, column=1, sticky="w")
            self.invoice_item_table_total.grid(row=3, column=2, sticky="w")
            
        def _bind_controls():
            self.bind("<Control-n>", lambda e: self.invoice_item_table.add_row(values=None))
            self.bind("<Delete>", lambda e: self.invoice_item_table.delete_row())
            self.invoice_item_table.bind("<<RowChange>>", lambda e: self._update_invoice_item_table_total())
            self.invoice_form.amount_widget.bind("<KeyRelease>", lambda e: self._update_invoice_item_table_total())
            self.bind("<F1>", self.invoice_item_table._cat_on_f1)
            self.bind("<F2>", lambda e: self.invoice_item_table._open_editor_by_col("description"))
            self.bind("<F3>", lambda e: self.invoice_item_table._open_editor_by_col("quantity"))
            self.bind("<F4>", lambda e: self.invoice_item_table._open_editor_by_col("amount"))

        _grid_ui_elements()
        _bind_controls()


    @cached_property
    def header(self):
        self._invoice_template_name_var = tk.StringVar()

        def _select_invoice_template(event):
            template_name = self._invoice_template_name_var.get()
            with get_connection("ldr") as conn:
                invoice_template_items = pd.read_sql_query(text("SELECT [DisplayOrder] AS [#], [CategoryDisplayName] AS [Category], [Description], [Quantity], [Amount] FROM [v_InvoiceTemplateItem] WHERE [InvoiceTemplateName] = :template_name ORDER BY [#]"), conn, params={"template_name": template_name})
            self.invoice_item_table.data = invoice_template_items
            self.invoice_form.amount = round(Decimal(str(pd.to_numeric(self.invoice_item_table.data["Amount"], errors="coerce").fillna(0).sum())), 2)
            self.invoice_form.amount_widget.event_generate("<KeyRelease>")
            self._update_invoice_item_table_total()

        frame = ttk.Frame(self)
        ttk.Label(frame, text="Invoice Data").grid(row=0, column=0, padx=10, pady=10, sticky="w")

        combo_frame = ttk.Frame(self)
        combo_frame.grid(row=1, column=1, padx=(0,10), pady=10, sticky='w')

        ttk.Label(combo_frame, text="Invoice Template:").grid(row=0,column=0, padx=(0,10))
        invoice_template_combobox = ttk.Combobox(combo_frame, values=data.InvoiceTemplates()["InvoiceTemplateName"].to_list(), state="readonly", textvariable=self._invoice_template_name_var, width=40)
        invoice_template_combobox.grid(row=0, column=1)
        invoice_template_combobox.bind("<<ComboboxSelected>>", _select_invoice_template)
        return frame
    

    @cached_property
    def invoice_item_table_total(self):
        self._invoice_item_table_total_var = tk.StringVar(value="0.00")
        label = ttk.Label(self, textvariable=self._invoice_item_table_total_var)
        label.configure(font=(FONT, 24, 'bold'))
        return label


    @cached_property
    def invoice_item_table(self) -> InvoiceItemTable:
        """ Table for displaying invoice items """

        def _amount_validator(value) -> str:
            try:
                cleaned_value = str(value).strip()
                if not re.fullmatch(r"-?(?:\d*\.\d{1,2}|\d+)", cleaned_value):
                    raise ValueError
                return f"{Decimal(cleaned_value):.2f}"
            except ValueError:
                raise ValueError("Expected format: 0.00")

        def _quantity_validator(value) -> str:
            try:
                cleaned_value = str(value).strip()
                if not re.fullmatch(r"-?(?:\d*\.\d{1,3}|\d+)", cleaned_value):
                    raise ValueError
                return f"{Decimal(cleaned_value):.3f}"
            except ValueError:
                raise ValueError("Expected format: 0.000")
            
        invoice_item_table = InvoiceItemTable(self)
        invoice_item_table.set_validator("Amount", _amount_validator)
        invoice_item_table.set_validator("Quantity", _quantity_validator) 
        return invoice_item_table
    

    @cached_property
    def invoice_item_table_controls(self):
        frame = ttk.Frame(self)
        add_item_button = ttk.Button(frame, text="Add Item", command=self.invoice_item_table.add_row)
        add_item_button.grid(row=0, column=0, padx=5)
        delete_item_button = ttk.Button(frame, text="Delete Item", command=self.invoice_item_table.delete_row)
        delete_item_button.grid(row=0, column=1, padx=(0,5))
        return frame
    

    def _table_total_matches_invoice_total(self) -> bool:
        total = round(Decimal(str(pd.to_numeric(self.invoice_item_table.data["Amount"], errors="coerce").fillna(0).sum())), 2)
        total_amount_due = round(Decimal(self.invoice_form.amount_widget.get()), 2) if self.invoice_form.amount_widget.get() else round(Decimal(0), 2)
        return total == total_amount_due

    def _update_invoice_item_table_total(self):
        total = round(Decimal(str(pd.to_numeric(self.invoice_item_table.data["Amount"], errors="coerce").fillna(0).sum())), 2)
        self._invoice_item_table_total_var.set(f"{total:.2f}")
        if self._table_total_matches_invoice_total():
            self.invoice_item_table_total.configure(foreground=SUCCESS)
        else:
            self.invoice_item_table_total.configure(foreground=DANGER)

    def _save(self):
        """Connection is passed in so that the insert can be executed within an existing transaction. That way if a part fails data integrity is maintained."""
        inv = self.invoice_form.get()

        invoice_id = str(uuid.uuid4())
        invoice_data = {
            "InvoiceId":invoice_id,
            "PayeeId":data.get_payee_id(inv['payee']),
            "InvoiceDate":inv['invoice_date'],
            "DueDate":inv['due_date'],
            "InvoiceNumber":inv['invoice_number'],
            "Amount":inv['amount'],
            "Description":inv['description'],
            "StartDate":inv['start_date'],
            "EndDate":inv['end_date'],
            "ImageId":self.statement_item.ImageId
        }

        invoice_items = self.invoice_item_table.data
        invoice_items = invoice_items.rename(columns={"#":"DisplayOrder"})  
        invoice_items['InvoiceId'] = invoice_id
        invoice_items['CategoryId'] = invoice_items['Category'].apply(lambda x: data.get_category_id(x) if pd.notna(x) else None)
        invoice_items = invoice_items.drop(columns=['Category'])
        invoice_items['InvoiceItemId'] = [str(uuid.uuid4()) for _ in range(len(invoice_items))]

        try:

            if not self._table_total_matches_invoice_total():
                messagebox.showerror("Invoice total does not match","The total of the invoice items does not match the total amount due. Please adjust the amounts to match before saving.")
                return None
            
            if not invoice_data['PayeeId']:
                messagebox.showerror("Unspecified Payee","Please specify payee")
                return None
            
            if not invoice_data['InvoiceDate']:
                messagebox.showerror("Unspecified Invoice Date","Please specify invoice_date")
                return None
            
            if not invoice_data['Amount']:
                messagebox.showerror("Unspecified amount","Please specify Invoice Total Amount")
                return None
        
            with get_connection("ldr") as conn:
                data.insert_invoice(conn, invoice_data, invoice_items)
                data.update_image_sort_status(conn, self.statement_item.ImageId, 'c')
                data.update_statement_item_invoice_id(conn, invoice_id, self.statement_item.StatementItemId)

            self._close_callback()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice: {str(e)}")
            return None