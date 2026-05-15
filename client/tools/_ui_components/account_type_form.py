from tkinter import ttk
from gui import Form, StringField


class AccountTypeForm(Form):

    type_name = StringField(
        label="Type Name:",
        row=0, col=0,
        colspan=2,
    )

    is_credit = StringField(
        label="Is Credit:",
        widget="combobox",
        values=["Yes", "No"],
        row=1, col=0,
        colspan=2,
    )

    description = StringField(
        label="Description:",
        row=2, col=0,
        colspan=2,
    )

    type_name_widget: ttk.Entry
    is_credit_widget: ttk.Combobox
    description_widget: ttk.Entry
