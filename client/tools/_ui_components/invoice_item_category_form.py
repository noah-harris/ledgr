from gui import Form, StringField


class InvoiceItemCategoryForm(Form):

    segment = StringField(
        label="Segment:",
        row=0, col=0,
        colspan=2,
    )

    category = StringField(
        label="Category:",
        row=1, col=0,
        colspan=2,
    )

    sub_category = StringField(
        label="Sub Category:",
        row=2, col=0,
        colspan=2,
    )

    unit = StringField(
        label="Unit:",
        row=3, col=0,
        colspan=2,
    )

    display_order = StringField(
        label="Display Order:",
        row=4, col=0,
        colspan=2,
    )

    description = StringField(
        label="Description:",
        row=5, col=0,
        colspan=2,
    )
