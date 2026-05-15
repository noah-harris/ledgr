import tkinter as tk
from config import *
from style import CARD, SURFACE_ALT
from gui import Modal
from models.Invoice import Invoice
from tools._ui_components import InvoiceCard

class InvoiceViewer(Modal):

    def __init__(self, master:tk.Tk, invoice_id:str=None):
        super().__init__(master, background_color=CARD, border_thickness=1, border_color=SURFACE_ALT)
        InvoiceCard(self, Invoice(invoice_id), show_receipts=True).pack(fill="both", expand=True)
