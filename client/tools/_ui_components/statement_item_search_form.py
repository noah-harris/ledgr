
from tkinter import ttk
import data
from gui import Form, StringField, DecimalField, DateTimeField

class StatementItemSearchForm(Form):

    account = StringField(
        label="Account:",
        widget="combobox",
        values=[""] + data.Account()["AccountDisplayName"].tolist(),
        row=0, col=0
    )

    method = StringField(
        label="Method:",
        widget="combobox",
        values=[""] + data.v_Method()["MethodDisplayName"].tolist(),
        row=0, col=2
    )

    payee = StringField(
        label="Payee:",
        widget="combobox",
        values=[""] + data.Payee()["PayeeName"].tolist(),
        row=0, col=4
    )

    transaction_date = DateTimeField(
        label="Transaction Date (YYYY-MM-DD):",
        time_label="Time (HH:MM:SS):",
        row=0, col=6, time_col=8
    )
    
    amount = DecimalField(
        label="Amount:",
        row=0, col=10
    )

    account_widget:ttk.Combobox
    method_widget:ttk.Combobox
    payee_widget:ttk.Combobox
    transaction_date_widget:ttk.Entry
    transaction_date_time_widget:ttk.Entry
    amount_widget:ttk.Entry
    
    def __init__(self, master):
        super().__init__(master)
        self.method_widget.config(values=[""])
        self.account_widget.bind("<<ComboboxSelected>>", lambda e: self._update_method_values(), add="+")

    def _update_method_values(self):
        df = data.v_Method()
        methods = df[df["AccountDisplayName"] == self.account]["MethodDisplayName"].tolist()
        self.method_widget.config(values=[""] + methods)

        