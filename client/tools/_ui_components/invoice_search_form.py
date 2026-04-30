from tkinter import ttk
import data
from gui import Form, StringField, DecimalField, DateField, DateTimeField

class InvoiceSearchForm(Form):

    payee = StringField(
        label="Payee:",
        widget="combobox",
        values=data.Payee()["PayeeName"].tolist(),
        row=0, col=0,
    )

    invoice_date = DateTimeField(
        label="Date (YYYY-MM-DD):",
        time_label="Time (HH:MM:SS):",
        row=0, col=2, time_col=4,
    )

    due_date = DateField(
        label="Due Date (YYYY-MM-DD):",
        row=0, col=6,
    )

    invoice_number = StringField(
        label="Invoice Number:",
        row=0, col=8,

    )

    amount = DecimalField(
        label="Amount:",
        row=0, col=10,

    )

    payee_widget:ttk.Combobox
    invoice_date_widget:ttk.Entry
    invoice_date_time_widget:ttk.Entry
    due_date_widget:ttk.Entry
    invoice_number_widget:ttk.Entry
    amount_widget:ttk.Entry
