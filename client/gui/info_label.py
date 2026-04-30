import tkinter as tk
from tkinter import ttk

class InfoLabel(ttk.Frame):

    def __init__(self, master:tk.Widget, name:str, var:tk.StringVar=None, value=None):
        """
            An object who can have its data changes. value must be castable to string.
        """
        super().__init__(master)
        self._name = name
        self._value_string_var = tk.StringVar(master, "") if var is None else var

        self.value = value
        name_label = ttk.Label(self, text=name, font="bold")
        value_label = ttk.Label(self, textvariable=self._value_string_var, anchor="e")

        self.grid_columnconfigure(1, weight=1)
        name_label.grid(row=0, column=0, sticky="e")
        value_label.grid(row=0, column=1, sticky="ew")

    @property
    def name(self):
        return self._name
    
    @property
    def value(self):
        return self._value_string_var.get()

    @value.setter
    def value(self, val):
        if val is None:
            new_value = ""
        try:
            new_value = str(val)
        except Exception as e:
            raise ValueError("Value must be castable to string. ERROR= " + str(e))
        self._value_string_var.set(new_value)


    def var(self):
        return self._value_string_var