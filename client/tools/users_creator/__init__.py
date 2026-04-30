from functools import cached_property
import uuid
import pandas as pd

from tools import Tool
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from .._ui_components.users_form import UsersForm
from db import get_connection

class UsersCreator(Tool):
    def __init__(self, master:tk.Tk):
        super().__init__(master, title="Create User", geometry="500x200")
        self.users_form
        ttk.Button(self, text="Create User", command=self._handle_create_user).grid(row=1, column=0, pady=10)

  
    @cached_property
    def users_form(self):
        users_form = UsersForm(self)
        users_form.grid(row=0, column=0)
        return users_form
    
    def _handle_create_user(self):
        user_data:dict = self.users_form.get()
        user_data["UsersId"] = str(uuid.uuid4())

        try:
            df = pd.DataFrame([user_data])
            with get_connection() as conn:
                df.to_sql("Users", conn, if_exists="append", index=False)
            messagebox.showinfo("Success", "User created successfully!")
            self.destroy()
        except:
            messagebox.showerror("Error", "Failed to create user!")
