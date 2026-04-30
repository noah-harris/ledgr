from functools import cached_property
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

from .._ui_components.account_form import AccountForm
from tools import Tool

class AccountCreator(Tool):
    def __init__(self, master:tk.Tk):
        super().__init__(master)
        self.account_form
        ttk.Button(self, text="Create Account", command=self._create_account).grid(row=1, column=0, padx=10, pady=10)
        
    @cached_property
    def account_form(self):
        account_form = AccountForm(self)
        account_form.grid(row=0, column=0, padx=10, pady=10)
        return account_form
    
    def _create_account(self):
        account_data = self.account_form.get()
        messagebox.showinfo("Account Created", f"Account for {account_data} created successfully!")

        
       # Add logic to create account using account_data 