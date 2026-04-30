import tkinter as tk
from tkinter import ttk
from uuid import UUID


class InvoiceEditor(tk.Toplevel):
    
    def __init__(self, master:tk.Tk, transaction_id:UUID):
        super().__init__(master)
        self.title("Edit Invoice Details")
        self.state('zoomed')

        ttk.Label(self, text="Edit Invoice Details").pack(pady=20)
        # Add more widgets for editing invoice details here