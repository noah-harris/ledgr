from tkinter import ttk
import data
from gui import Form, StringField, DateField

class AccountForm(Form):

    users = StringField(
        label="User:",
        widget="combobox",
        values=data.Users()["FullName"].tolist(),
        row=0, col=0,
        colspan=2,
    )

    organization = StringField(
        label="Organization:",
        row=1, col=0,
        widget="combobox",
        values=data.BankOrganization()["OrganizationName"].tolist(),
        colspan=2,
    )

    account_type = StringField(
        label="Account Type:",
        widget="combobox",
        values=data.AccountType()["AccountTypeName"].tolist(),
        row=2, col=0,
        colspan=2,
    )

    account_number = StringField(
        label="Account Number:",
        row=3, col=0,
        colspan=2,
    )

    start_date = DateField(
        label="Start Date:",
        default_time="00:00:00",
        row=4, col=0,
        colspan=2,
    )

    end_date = DateField(
        label="End Date:",
        default_time="23:59:59",
        row=5, col=0,
        colspan=2,
    )

    description = StringField(
        label="Description:",
        row=6, col=0,
        colspan=2,
    )

    users_widget:ttk.Combobox
    organization_widget:ttk.Combobox
    account_type_widget:ttk.Combobox
    account_number_widget:ttk.Entry 
    start_date_widget:ttk.Entry
    end_date_widget:ttk.Entry
    description_widget:ttk.Entry