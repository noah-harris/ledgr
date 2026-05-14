from models.Invoice import Invoice
from tkinter import ttk
from config import *
from pathlib import Path
from gui import ImageViewer, Table, get_image_size_from_bytes
from style import FONT, PRIMARY_DARKER
from .statement_item_card import StatementItemCard
from resolve_image_bytes import resolve_image_bytes

class InvoiceCard(ttk.Frame):
    def __init__(self, master, invoice:Invoice, show_receipts:bool=True):
        super().__init__(master, style='Card.TFrame')
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


class HeaderDescription(ttk.Frame):

    def __init__(self, master, invoice: Invoice):
        super().__init__(master, style='Bordered.Card.TFrame')
        ttk.Label(self, text="DESCRIPTION", style='Card.Muted.TLabel', font=(FONT, 8)).pack(anchor='w', padx=12, pady=(10, 2))
        ttk.Label(self, text=f"{invoice.InvoiceDescription}", style='Card.TLabel', font=(FONT, 10), wraplength=700, justify="left").pack(anchor='w', padx=12, pady=(0, 10))


class Header(ttk.Frame):

    def __init__(self, master, invoice: Invoice):
        super().__init__(master, style='Subtle.TFrame')
        accent = ttk.Frame(self, style='Primary.TFrame', width=4)
        accent.pack(side="left", fill="y")
        self.content = ttk.Frame(self, style='Subtle.TFrame')
        self.content.pack(side="left", fill="both", expand=True, padx=16, pady=14)
        self._right_column(invoice)
        self._left_column(invoice)


    def _left_column(self, invoice: Invoice):
        left_col = ttk.Frame(self.content, style='Subtle.TFrame')
        left_col.pack(side="left", fill="both", expand=True)
        line_1_text = f"INVOICE · {invoice.InvoiceNumber or f'{invoice.PayeeName}-{invoice.InvoiceDate.strftime('%Y%m%d')}'}"
        line_2_text = invoice.PayeeName.title()
        line_3_text =f"{'singleworddetail'.title()} · {invoice.InvoiceDate.strftime('%m/%d/%Y %I:%M:%S %p')}"
        ttk.Label(left_col, text=line_1_text, font=(FONT, 8), style='Subtle.Muted.TLabel').pack(anchor="w")
        ttk.Label(left_col, text=line_2_text, font=(FONT, 14, 'bold'), style='Subtle.TLabel').pack(anchor="w")
        ttk.Label(left_col, text=line_3_text, font=(FONT, 8), style='Subtle.Muted.TLabel').pack(anchor="w")

        if None not in [invoice.StartDate, invoice.EndDate, invoice.DueDate]:
            line_4_optional_text = f"{invoice.StartDate.strftime('%b %d')} - "f"{invoice.EndDate.strftime('%b %d, %Y')} · "f"Due {invoice.DueDate.strftime('%b %d')}"
            ttk.Label(left_col, text=line_4_optional_text, font=(FONT, 9), style='Subtle.Muted.TLabel').pack(anchor="w")


    def _right_column(self, invoice: Invoice):
        right_col = ttk.Frame(self.content, style='Subtle.TFrame')
        right_col.pack(side="right", fill="y")
        total_amount_title_text = f"TOTAL DUE"
        total_amount_text = f"${str(invoice.Amount)}"
        ttk.Label(right_col, text=total_amount_title_text, font=(FONT, 14, 'bold'), foreground=PRIMARY_DARKER, style='Subtle.TLabel').pack(expand=True)
        ttk.Label(right_col, text=total_amount_text, font=(FONT, 14), foreground=PRIMARY_DARKER, style='Subtle.TLabel').pack(expand=True)


class InvoicePanel(ttk.Frame):

    def __init__(self, master, invoice:Invoice):
        super().__init__(master, style='Card.TFrame')
        self.table = self._table(invoice)
        self.image = self._image(invoice)
        self.table.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        self.image.grid(row=0, column=1, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)


    def _table(self, invoice: Invoice):
        from style import BORDER_STRONG
        table = Table(self, border={'color': BORDER_STRONG, 'thickness': 1}, columns={
            "#":           {"width": 20},
            "Category":    {"justify": "left"},
            "Description": {"justify": "left"},
            "Qty":         {"width": 50},
            "Amt":         {"width": 60, "justify": "right"},
        })
        table.data = invoice.InvoiceItems
        return table


    def _image(self, invoice: Invoice):
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


class PaymentPanel(ttk.Frame):

    def __init__(self, master, invoice:Invoice):
        super().__init__(master, style='Card.TFrame')
        self._invoice = invoice
        ttk.Label(self, text="Payments", font=(FONT, 12, 'bold'), style='Card.TLabel').pack(anchor='w')
        self._build()


    def _build(self):
        for item in self._invoice.StatementItems:
            panel = StatementItemCard(self, item)
            panel.pack(fill="x", pady=(10, 0))
