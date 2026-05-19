from tkinter import ttk
import data
from gui import Form, StringField, DecimalField, DateField, DateTimeField


class StatementItemForm(Form):

    payee = StringField(
        label="Payee:", widget="combobox",
        values=lambda: data.Payee()["PayeeName"].tolist(),
        row=0, col=0, colspan=2,
    )
    method = StringField(
        label="Method:", widget="combobox",
        values=lambda: data.v_Method()["MethodDisplayName"].tolist(),
        row=1, col=0, colspan=2,
    )
    transaction_date = DateTimeField(
        label="Transaction Date (YYYY-MM-DD):", time_label="Time (HH:MM:SS):",
        row=2, col=0, time_col=2,
    )
    post_date = DateField(label="Post Date (YYYY-MM-DD):", row=3, col=0)
    reference_number = StringField(label="Reference Number:", row=4, col=0, colspan=2)
    amount = DecimalField(label="Amount:", row=5, col=0, colspan=2)
    description = StringField(label="Description:", row=6, col=0, colspan=2)

    payee_widget: ttk.Combobox
    method_widget: ttk.Combobox
    transaction_date_widget: ttk.Entry
    transaction_date_time_widget: ttk.Entry
    post_date_widget: ttk.Entry
    reference_number_widget: ttk.Entry
    amount_widget: ttk.Entry
    description_widget: ttk.Entry
