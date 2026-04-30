
from tkinter import ttk
import data
from gui import Form, StringField, DecimalField, DateTimeField

class AccountTransferForm(Form):

    account_from = StringField(
        label="Account From:",
        widget="combobox",
        values=[""] + data.Account()["AccountDisplayName"].tolist(),
        row=0, col=0
    )

    method_from = StringField(
        label="Method From:",
        widget="combobox",
        values=[""] + data.v_Method()["MethodDisplayName"].tolist(),
        row=0, col=2
    )

    account_to = StringField(
        label="Account To:",
        widget="combobox",
        values=[""] + data.Account()["AccountDisplayName"].tolist(),
        row=1, col=0
    )

    method_to = StringField(
        label="Method To:",
        widget="combobox",
        values=[""] + data.v_Method()["MethodDisplayName"].tolist(),
        row=1, col=2
    )

    transfer_amount = DecimalField(
        label="Transfer Amount:",
        row=2, col=0
    )

    transfer_fee_amount = DecimalField(
        label="Transfer Fee Amount:",
        row=2, col=2
    )
    
    transaction_date = DateTimeField(
        label="Transaction Date:",
        row=3, col=0, time_col=2
    )


    account_from_widget:ttk.Combobox
    method_from_widget:ttk.Combobox
    account_to_widget:ttk.Combobox
    method_to_widget:ttk.Combobox
    transaction_date_widget:ttk.Entry
    transaction_date_time_widget:ttk.Entry
    transfer_amount_widget:ttk.Entry
    transfer_fee_amount_widget:ttk.Entry
    
    def __init__(self, master):
        super().__init__(master)

        self.method_from_widget.config(values=[""])
        self.method_to_widget.config(values=[""])

        self.account_from_widget.bind("<<ComboboxSelected>>", lambda e: _update_method_from_values(), add="+")
        self.account_to_widget.bind("<<ComboboxSelected>>", lambda e: _update_method_to_values(), add="+")

        def _update_method_from_values():
            account = self.account_from_widget.get()
            df = data.v_Method()
            methods = df[(df["AccountDisplayName"] == account)*(df["IsAccountTransferMethod"])]["MethodDisplayName"].tolist()
            self.method_from_widget.config(values=[""] + methods)
            self.method_from_widget.set("")

        def _update_method_to_values():
            account = self.account_to_widget.get()
            df = data.v_Method()
            methods = df[(df["AccountDisplayName"] == account)*(df["IsAccountTransferMethod"])]["MethodDisplayName"].tolist()
            self.method_to_widget.config(values=[""] + methods)
            self.method_to_widget.set("")
