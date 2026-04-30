import tkinter as tk
from tkinter import ttk

from tools.users_creator import UsersCreator
from tools.account_creator import AccountCreator
from tools.statement_loader import StatementLoader
from tools.statement_viewer import StatementViewer
from tools.organization_creator import OrganizationCreator
from tools.invoice_manager import InvoiceManager
from tools.image_linker import ImageLinker
from tools.transaction_linker import StatementItemInvoiceLinker

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Ledgr v1.0.0.0")
        self.state('zoomed')

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True)
        label = ttk.Label(frame, text="Tools will be listed here")
        label.pack(pady=20)

        menubar = tk.Menu(self)
        menubar.add_command(label="View Invoice", command=lambda: InvoiceManager(self))

        user_menu = tk.Menu(menubar, tearoff=0)
        user_menu.add_command(label="Create", command=lambda: UsersCreator(self))
        menubar.add_cascade(label="Users", menu=user_menu)

        account_menu = tk.Menu(menubar, tearoff=0)
        account_menu.add_command(label="Create Account", command=lambda: AccountCreator(self))
        account_menu.add_command(label="Create Statement", command=lambda: StatementLoader(self))
        account_menu.add_command(label="View Statement", command=lambda: StatementViewer(self))
        menubar.add_cascade(label="Account", menu=account_menu)

        misc_menu = tk.Menu(menubar, tearoff=0)
        misc_menu.add_command(label="Organization", command=lambda: OrganizationCreator(self))
        menubar.add_cascade(label="Misc", menu=misc_menu)

        tool_menu = tk.Menu(menubar, tearoff=0)
        tool_menu.add_command(label="Sort Images", command=lambda: ImageLinker(self))
        tool_menu.add_command(label="Statement Item / Invoice Linker", command=lambda: StatementItemInvoiceLinker(self))

        menubar.add_cascade(label="Tools", menu=tool_menu)
    
        self.config(menu=menubar)
        self.mainloop()