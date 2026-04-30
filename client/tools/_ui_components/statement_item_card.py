from models.Invoice import StatementItem
import tkinter as tk
from config import *
from gui import ImageViewer
from color import *

class StatementItemCard(tk.Frame):
    def __init__(self, master, statement_item:StatementItem):
        super().__init__(master, bg=WHITE, highlightthickness=1, highlightbackground=BLACK, highlightcolor=BLACK)
        self._statement_item = statement_item

        left_frame = tk.Frame(self, bg=WHITE)
        _line_1_text = f"{statement_item.AccountOrganizationName.title()} · {statement_item.PaymentDisplayNumber} · {statement_item.MethodTypeName.upper()}"
        _line_2_text = f"Trans {statement_item.TransactionDate.strftime('%m/%d/%Y %I:%M:%S %p')} · Posted {statement_item.PostDate.strftime('%m/%d/%Y')}{' · ' + statement_item.ReferenceNumber if statement_item.ReferenceNumber else ''}"
        tk.Label(left_frame, text=_line_1_text, font=("Segoe UI", 10), bg=WHITE).pack(anchor='w')
        tk.Label(left_frame, text=_line_2_text, font=("Segoe UI", 8), fg="gray", bg=WHITE).pack(anchor='w')

        right_frame = tk.Frame(self, bg=WHITE)        
        tk.Button(right_frame, text="View Receipt", command=self._view_receipt, bg=LIGHT_BLUE_BACKGROUND, fg=BLUE_SMALL_TEXT, activebackground=DARK_BLUE_BACKGROUND, activeforeground=WHITE, relief="flat", bd=0, highlightthickness=0).pack(side='right', padx=(0, 10))
        tk.Label(right_frame, text=f"{statement_item.Amount}", font=("Segoe UI", 10, "bold"), bg=WHITE).pack(side='right', padx=(0, 10))

        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=10)

    def _view_receipt(self):
        from pathlib import Path
        window = tk.Toplevel(self)
        window.title("Receipt Image")
        viewer = ImageViewer(window, show_nav_buttons=False)
        img_bytes = fetch_image_bytes(self._statement_item.ImageFileName)
        if img_bytes is None:
            viewer.show_placeholder("Image unavailable")
        else:
            filename = self._statement_item.ImageFileName
            viewer.load_from_bytes(img_bytes, Path(filename).suffix.lstrip("."), Path(filename).stem)
        viewer.pack(fill="both", expand=True)