import tkinter as tk
from tkinter import ttk

import style
from tools.users_creator import UsersCreator
from tools.account_creator import AccountCreator
from tools.statement_loader import StatementLoader
from tools.statement_viewer import StatementViewer
from tools.organization_creator import OrganizationCreator
from tools.invoice_manager import InvoiceManager
from tools.image_linker import ImageLinker
from tools.transaction_linker import StatementItemInvoiceLinker
from tools.invoice_item_category_manager import InvoiceItemCategoryManager
from tools.image_uploader import ImageUploader
from tools.invoice_template_creator import InvoiceTemplateCreator
from tools.data_fix_logger import DataFixLogger
from tools.statement_item_search import StatementItemSearch

class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Ledgr v1.0.0.0")
        self.state('zoomed')
        style.apply_styles(self)

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
        account_menu.add_command(label="Edit", command=lambda: AccountCreator(self))
        menubar.add_cascade(label="Account", menu=account_menu)

        statement_menu = tk.Menu(menubar, tearoff=0)
        statement_menu.add_command(label="Create", command=lambda: StatementLoader(self))
        statement_menu.add_command(label="View & Edit", command=lambda: StatementViewer(self))
        statement_menu.add_command(label="Search Items", command=lambda: StatementItemSearch(self))
        menubar.add_cascade(label="Statement", menu=statement_menu)

        organization_menu = tk.Menu(menubar, tearoff=0)
        organization_menu.add_command(label="Edit", command=lambda: OrganizationCreator(self))
        menubar.add_cascade(label="Organization", menu=organization_menu)

        tool_menu = tk.Menu(menubar, tearoff=0)
        tool_menu.add_command(label="Sort Images", command=lambda: ImageLinker(self))
        tool_menu.add_command(label="Statement Item / Invoice Linker", command=lambda: StatementItemInvoiceLinker(self))
        tool_menu.add_command(label="Image Uploader", command=lambda: ImageUploader(self))
        tool_menu.add_command(label="Invoice Item Categories", command=lambda: InvoiceItemCategoryManager(self))
        tool_menu.add_command(label="Invoice Templates", command=lambda: InvoiceTemplateCreator(self))
        tool_menu.add_command(label="Data Fix Log", command=lambda: DataFixLogger(self))

        menubar.add_cascade(label="Tools", menu=tool_menu)

        menu_style = dict(
            bg=style.PRIMARY, fg=style.TEXT_LIGHT,
            activebackground=style.HOVER, activeforeground=style.TEXT_LIGHT,
            relief='flat', borderwidth=0,
        )
        menubar.configure(**menu_style)
        for m in [user_menu, account_menu, organization_menu, tool_menu, statement_menu]:
            m.configure(**menu_style)

        self.config(menu=menubar)
        self.mainloop()