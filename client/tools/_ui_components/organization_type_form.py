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
    category = StringField(
        label="Category:",
        widget="combobox",
        values=[],
        row=3, col=0, colspan=2,
    )
    description = StringField(
        label="Description:",
        row=4, col=0, colspan=2,
    )

    type_name_widget: ttk.Entry
    is_account_provider_widget: ttk.Combobox
    segment_widget: ttk.Combobox
    category_widget: ttk.Combobox
    description_widget: ttk.Entry

    def __init__(self, master):
        super().__init__(master)
        df = data.InvoiceItemCategory()
        self._categories_by_segment = (
            df.groupby("Segment")["Category"]
            .apply(lambda s: sorted(s.drop_duplicates().tolist()))
            .to_dict()
        )
        self.segment_widget.bind("<<ComboboxSelected>>", self._on_segment_selected, add="+")

    def _on_segment_selected(self, _event=None):
        self._update_category_options(self.segment_widget.get(), clear=True)

    def _update_category_options(self, segment: str, clear: bool = True):
        categories = self._categories_by_segment.get(segment, [])
        self.category_widget.config(values=categories)
        self.category_widget._all_values = categories
        if clear:
            self.category_widget.set("")
