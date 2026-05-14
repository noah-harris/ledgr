from tkinter import ttk
import data
from gui import Form, StringField


def _segment_values() -> list[str]:
    return data.InvoiceItemCategory()["Segment"].drop_duplicates().sort_values().tolist()


class OrganizationTypeForm(Form):
    type_name = StringField(
        label="Type Name:",
        row=0, col=0, colspan=2,
    )
    is_account_provider = StringField(
        label="Is Account Provider:",
        widget="combobox",
        values=["Yes", "No"],
        row=1, col=0, colspan=2,
    )
    segment = StringField(
        label="Segment:",
        widget="combobox",
        values=_segment_values,
        row=2, col=0, colspan=2,
    )
    description = StringField(
        label="Description:",
        row=3, col=0, colspan=2,
    )

    type_name_widget: ttk.Entry
    is_account_provider_widget: ttk.Combobox
    segment_widget: ttk.Combobox
    description_widget: ttk.Entry
