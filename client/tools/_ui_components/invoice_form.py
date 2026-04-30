from tkinter import ttk
import data
from gui import Form, StringField, DecimalField, DateField, DateTimeField

class InvoiceForm(Form):

    payee = StringField(
        label="Payee:",
        widget="combobox",
        values=data.Payee()["PayeeName"].tolist(),
        row=0, col=0,
        colspan=2,
    )

    invoice_date = DateTimeField(
        label="Date (YYYY-MM-DD):",
        time_label="Time (HH:MM:SS):",
        row=1, col=0, time_col=2,
    )

    due_date = DateField(
        label="Due Date (YYYY-MM-DD):",
        row=2, col=0,
    )

    invoice_number = StringField(
        label="Invoice Number:",
        row=3, col=0,
        colspan=2,
    )

    amount = DecimalField(
        label="Amount:",
        row=4, col=0,
        colspan=2,
    )

    start_date = DateField(
        label="Start Date:",
        default_time="00:00:00",
        row=5, col=0,
        colspan=2,
    )

    end_date = DateField(
        label="End Date:",
        default_time="23:59:59",
        row=6, col=0,
        colspan=2,
    )

    description = StringField(
        label="Description:",
        row=7, col=0,
        colspan=2,
    )

    payee_widget:ttk.Combobox
    invoice_date_widget:ttk.Entry
    invoice_date_time_widget:ttk.Entry
    due_date_widget:ttk.Entry
    invoice_number_widget:ttk.Entry
    amount_widget:ttk.Entry
    start_date_widget:ttk.Entry
    end_date_widget:ttk.Entry
    description_widget:ttk.Entry

