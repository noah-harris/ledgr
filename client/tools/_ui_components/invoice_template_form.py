from tkinter import ttk

import data
from gui import Form, StringField


class InvoiceTemplateForm(Form):

    template_name = StringField(
        label="Template Name:",
        row=0, col=0,
        colspan=2,
    )

    payee = StringField(
        label="Payee:",
        widget="combobox",
        values=[],
        row=1, col=0,
        colspan=2,
        width=35,
    )

    template_name_widget: ttk.Entry
    payee_widget: ttk.Combobox
