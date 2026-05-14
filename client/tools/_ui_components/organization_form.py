from tkinter import ttk
import data
from gui import Form, StringField


class OrganizationForm(Form):
    name = StringField(
        label="Organization Name:",
        row=0, col=0, colspan=2,
    )
    org_type = StringField(
        label="Organization Type:",
        widget="combobox",
        values=lambda: data.OrganizationTypes()["OrganizationTypeName"].tolist(),
        row=1, col=0, colspan=2,
    )
    description = StringField(
        label="Description:",
        row=2, col=0, colspan=2,
    )

    name_widget: ttk.Entry
    org_type_widget: ttk.Combobox
    description_widget: ttk.Entry
