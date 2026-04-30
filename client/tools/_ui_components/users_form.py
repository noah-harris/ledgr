from tkinter import ttk
from gui import Form, StringField

class UsersForm(Form):

    username = StringField(
        label="Username:",
        row=0, col=0,
    )

    email = StringField(
        label="Email:",
        row=1, col=0,
    )

    firstname = StringField(
        label="First Name:",
        row=2, col=0,
    )

    lastname = StringField(
        label="Last Name:",
        row=2, col=2,
    )

    username_widget:ttk.Entry
    email_widget:ttk.Entry
    firstname_widget:ttk.Entry
    lastname_widget:ttk.Entry