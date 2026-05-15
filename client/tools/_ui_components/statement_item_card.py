from models.Invoice import StatementItem
import tkinter as tk
from tkinter import ttk
from config import *
from gui import ImageViewer
from resolve_image_bytes import resolve_image_bytes

class StatementItemCard(ttk.Frame):
    def __init__(self, master, statement_item:StatementItem):
        super().__init__(master, style='Bordered.Card.TFrame')
        self._statement_item = statement_item

        left_frame = ttk.Frame(self, style='Card.TFrame')
        _line_1_text = f"{statement_item.AccountOrganizationName.title()} · {statement_item.PaymentDisplayNumber} · {statement_item.MethodTypeName.upper()}"
        _line_2_text = f"Trans {statement_item.TransactionDate.strftime('%m/%d/%Y %I:%M:%S %p')} · Posted {statement_item.PostDate.strftime('%m/%d/%Y')}{' · ' + statement_item.ReferenceNumber if statement_item.ReferenceNumber else ''}"
        ttk.Label(left_frame, text=_line_1_text, style='Card.TLabel').pack(anchor='w')
        ttk.Label(left_frame, text=_line_2_text, style='Card.Muted.TLabel').pack(anchor='w')

        right_frame = ttk.Frame(self, style='Card.TFrame')
        ttk.Button(right_frame, text="View Receipt", command=self._view_receipt, style='Ghost.TButton').pack(side='right')
        ttk.Label(right_frame, text=f"{statement_item.Amount}", style='Card.Bold.TLabel').pack(side='right', padx=(0, 12))

        left_frame.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        right_frame.pack(side="right", fill="both", padx=(5, 10), pady=10)

    def _view_receipt(self):
        from pathlib import Path
        window = tk.Toplevel(self)
        window.title("Receipt Image")
        viewer = ImageViewer(window, show_nav_buttons=False)
        img_bytes = resolve_image_bytes(f"{IMAGE_DIRECTORY}/{self._statement_item.ImageFileName}")

        if img_bytes is None:
            viewer.show_placeholder("Image unavailable")
        else:
            filename = self._statement_item.ImageFileName
            viewer.load_from_bytes(img_bytes, Path(filename).suffix.lstrip("."), Path(filename).stem)
        viewer.pack(fill="both", expand=True)
