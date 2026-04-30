import tkinter as tk
from config import *
from color import *
from gui import Modal
from models.Invoice import Invoice
from tools._ui_components import InvoiceCard

class InvoiceViewer(Modal):

    def __init__(self, master:tk.Tk, invoice_id:str=None):
        super().__init__(master, background_color=WHITE, border_thickness=1, border_color=YELLOWISH)
        InvoiceCard(self, Invoice(invoice_id), show_receipts=True).pack(fill="both", expand=True)