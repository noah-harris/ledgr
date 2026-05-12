from models.Invoice import Invoice
import tkinter as tk
from config import *
from pathlib import Path
from gui import ImageViewer, Table, get_image_size_from_bytes
from color import *
from .statement_item_card import StatementItemCard
from resolve_image_bytes import resolve_image_bytes

class InvoiceCard(tk.Frame):
    def __init__(self, master, invoice:Invoice, show_receipts:bool=True):
        super().__init__(master, bg=WHITE)
        self._invoice:Invoice = invoice
        self._show_receipts = show_receipts
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.header = Header(self, invoice)
        self.header_description = HeaderDescription(self, invoice)
        self.invoice_panel = InvoicePanel(self, invoice)
       
        self.header.grid(row=0, column=0, sticky="ew")
        self.header_description.grid(row=1, column=0, sticky="ew", padx=10, pady=(10, 0))
        self.invoice_panel.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10, 0))

        if self._show_receipts:
            self.payment_panel = PaymentPanel(self, invoice)
            self.payment_panel.grid(row=3, column=0, sticky="ew", padx=10, pady=10)


class HeaderDescription(tk.Frame):
        
    def __init__(self, master, invoice: Invoice):
        super().__init__(master, bg="#FFFFFF", highlightthickness=1, highlightbackground=BLACK, highlightcolor=BLACK)
        description_title = "Description:"
        description_text = f"{invoice.InvoiceDescription}"
        tk.Label(self, text=description_title, font=("Segoe UI", 10, "bold"), fg=BLACK, bg=WHITE).pack(anchor='w')
        tk.Label(self, text=description_text, font=("Segoe UI", 8), fg=BLACK, bg=WHITE, wraplength=400, justify="left").pack(anchor='w')
        


class Header(tk.Frame):
        
    def __init__(self, master, invoice: Invoice):
        super().__init__(master, bg=LIGHT_BLUE_BACKGROUND)
        accent = tk.Frame(self, bg=BLUE_SMALL_TEXT, width=4)
        accent.pack(side="left", fill="y")
        self.content = tk.Frame(self, bg=LIGHT_BLUE_BACKGROUND)
        self.content.pack(side="left", fill="both", expand=True, padx=16, pady=14)
        self._right_column(invoice)
        self._left_column(invoice)
        

    def _left_column(self, invoice: Invoice):
        left_col = tk.Frame(self.content, bg=LIGHT_BLUE_BACKGROUND)
        left_col.pack(side="left", fill="both", expand=True)
        line_1_text = f"INVOICE · {invoice.InvoiceNumber or f'{invoice.PayeeName}-{invoice.InvoiceDate.strftime('%Y%m%d')}'}"
        line_2_text = invoice.PayeeName.title()
        line_3_text =f"{'singleworddetail'.title()} · {invoice.InvoiceDate.strftime('%m/%d/%Y %I:%M:%S %p')}"
        tk.Label(left_col, text=line_1_text, font=("Segoe UI", 8), fg=BLUE_SMALL_TEXT, bg=LIGHT_BLUE_BACKGROUND).pack(anchor="w")
        tk.Label(left_col, text=line_2_text, font=("Segoe UI", 14, "bold"), fg=BOLD_BLUE_TEXT, bg=LIGHT_BLUE_BACKGROUND).pack(anchor="w")
        tk.Label(left_col, text=line_3_text, font=("Segoe UI", 8), fg=BLUE_SMALL_TEXT, bg=LIGHT_BLUE_BACKGROUND).pack(anchor="w")

        # If it's a bill, show the due date and period (goes into left_col now).
        if None not in [invoice.StartDate, invoice.EndDate, invoice.DueDate]:
            line_4_optional_text = f"{invoice.StartDate.strftime('%b %d')} - "f"{invoice.EndDate.strftime('%b %d, %Y')} · "f"Due {invoice.DueDate.strftime('%b %d')}"
            tk.Label(left_col, text=line_4_optional_text, font=("Segoe UI", 9), fg=BLUE_SMALL_TEXT, bg=LIGHT_BLUE_BACKGROUND).pack(anchor="w")


    def _right_column(self, invoice: Invoice):
        right_col = tk.Frame(self.content, bg=LIGHT_BLUE_BACKGROUND)
        right_col.pack(side="right", fill="y")
        total_amount_title_text = f"TOTAL DUE"
        total_amount_text = f"${str(invoice.Amount)}"
        tk.Label(right_col, text=total_amount_title_text, font=("Segoe UI", 14, "bold"), fg=BOLD_BLUE_TEXT, bg=LIGHT_BLUE_BACKGROUND).pack(expand=True)
        tk.Label(right_col, text=total_amount_text, font=("Segoe UI", 14), fg=BOLD_BLUE_TEXT, bg=LIGHT_BLUE_BACKGROUND).pack(expand=True)



class InvoicePanel(tk.Frame):

    def __init__(self, master, invoice:Invoice):
        super().__init__(master, bg=WHITE)
        self.table = self._table(invoice)
        self.image = self._image(invoice)
        self.table.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        self.image.grid(row=0, column=1, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)   # table gets 1 share
        self.grid_columnconfigure(1, weight=3)   # image gets 3 shares


    def _table(self, invoice: Invoice):
        table = Table(self, border={'color':BLACK, 'thickness':1}, columns={
            "#": {"width":20}, "Category": {"width":200, 'justify':"left"}, "Description": {"width":200, 'justify':"left"}, "Qty": {"width":50}, "Amt": {"width":60, 'justify':"right"},
        })
        table.data = invoice.InvoiceItems
        return table
    

    def _image(self, invoice: Invoice):
        # img_bytes = fetch_image_bytes(invoice.ImageFileName)
        img_bytes = resolve_image_bytes(f"{IMAGE_DIRECTORY}/{invoice.ImageFileName}")
        if img_bytes is None:
            image = ImageViewer(self, show_nav_buttons=False)
            image.show_placeholder("Image unavailable")
            return image
        filetype = Path(invoice.ImageFileName).suffix.lstrip(".")
        stem = Path(invoice.ImageFileName).stem
        w, h = get_image_size_from_bytes(img_bytes, filetype)
        image = ImageViewer(self, show_nav_buttons=False, canvas_size=(w, min(h, 600)))
        image.load_from_bytes(img_bytes, filetype, stem)
        return image



class PaymentPanel(tk.Frame):
    
    def __init__(self, master, invoice:Invoice):
        super().__init__(master, bg=WHITE)
        self._invoice = invoice
        tk.Label(self, text="Payments", font=("Segoe UI", 12, "bold"), bg=WHITE).pack(anchor='w')
        self._build()


    def _build(self):
        for item in self._invoice.StatementItems:
            panel = StatementItemCard(self, item)
            panel.pack(fill="x", pady=(10, 0))


        

