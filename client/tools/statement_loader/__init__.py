from sqlalchemy import text
from functools import cached_property
import atexit
import os
import shutil
import tempfile
from pathlib import Path
from tkinter import messagebox, ttk
import webbrowser
import win32com.client
import pythoncom
from db import get_connection
import pandas as pd
from tools import Tool
import tkinter as tk
from config import *
from models import Image
from .._ui_components.image_selector import ImageSelector


class StatementLoader(Tool):

    STATEMENT_TOOL_EXCEL_PATH = Path(__file__).parent / "STATEMENT TOOL.xlsx"

    def __init__(self, master: tk.Tk, image: Image = None):
        super().__init__(master)

        ttk.Button(self, text="Upload Statement", command=self._save_statement).pack(pady=10)
        ttk.Button(self, text="Reopen Excel", command=self._reopen_excel).pack(pady=(0, 10))
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self._cleanup_and_close)

        if image is None:
            image = self._show_image_selector()

        if image is None or image.ImageId is None:
            logger.warning("No image selected.")
            self.destroy()
            self.master.state('zoomed')
            return

        self._image = image

        self._write_image_url_to_excel()

        webbrowser.open(self._image_url)
        os.startfile(self.temp_excel_tool_path)

        self.deiconify()

    # ──────────────────────────────────────────────────────────
    # IMAGE SELECTION
    # ──────────────────────────────────────────────────────────

    def _show_image_selector(self) -> Image | None:
        selector = ImageSelector(self)
        self.wait_window(selector)
        return selector.selected_image

    # ──────────────────────────────────────────────────────────
    # IMAGE URL
    # ──────────────────────────────────────────────────────────

    @property
    def _image_url(self) -> str:
        return f"{IMAGE_DIRECTORY}/{self._image.ImageFileName}"

    # ──────────────────────────────────────────────────────────
    # TEMP EXCEL
    # ──────────────────────────────────────────────────────────

    @cached_property
    def temp_excel_tool_path(self) -> Path:
        temp_dir = Path(tempfile.mkdtemp())
        atexit.register(shutil.rmtree, temp_dir, True)
        temp_file = temp_dir / self.STATEMENT_TOOL_EXCEL_PATH.name
        shutil.copy2(self.STATEMENT_TOOL_EXCEL_PATH, temp_file)
        return temp_file

    def _write_image_url_to_excel(self):
        pythoncom.CoInitialize()
        excel = None
        wb = None
        ws = None
        try:
            excel = win32com.client.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False
            wb = excel.Workbooks.Open(str(self.temp_excel_tool_path))
            ws = wb.Sheets("Statement Editor")
            ws.Range("C2").Value = self._image_url
            wb.Save()
            wb.Close(SaveChanges=False)
        finally:
            if wb is not None:
                del wb
            if ws is not None:
                del ws
            if excel is not None:
                excel.Quit()
                del excel
            pythoncom.CoUninitialize()

    def _reopen_excel(self):
        os.startfile(self.temp_excel_tool_path)

    def _cleanup_and_close(self):
        if 'temp_excel_tool_path' in self.__dict__:
            shutil.rmtree(self.temp_excel_tool_path.parent, ignore_errors=True)
        self.destroy()
        self.master.deiconify()
        self.master.state('zoomed')

    # ──────────────────────────────────────────────────────────
    # DATA
    # ──────────────────────────────────────────────────────────

    def get_data(self) -> pd.DataFrame:
        col_types = {"AccountId": "string", "StatementDate": "string", "StartDate": "string", "EndDate": "string", "StartBalance": "string", "EndBalance": "string", "PayeeId": "string", "MethodId": "string", "ReferenceNumber": "string", "Description": "string"}
        return pd.read_excel(self.temp_excel_tool_path, sheet_name="Output", dtype=col_types)

    # ──────────────────────────────────────────────────────────
    # SAVE
    # ──────────────────────────────────────────────────────────

    def _validate_statement(self) -> bool:
        if self.get_data()[["AccountId", "StatementDate", "StartDate", "EndDate", "StartBalance", "EndBalance", "MethodId", "PayeeId", "TransactionDate", "PostDate", "Amount"]].isnull().values.any():
            messagebox.showerror("Validation Error", "Statement item data contains null values in required fields. Please fill in all required fields.")
            return False
        return True

    def _save_statement(self):
        if not self._validate_statement():
            return

        statement_image_id = self._image.ImageId

        try:
            with get_connection("ldr") as conn:
                conn.execute(
                    text("UPDATE [Image] SET [ContentType]='STATEMENT', [StatusType]='c' WHERE [ImageId]=:image_id"),
                    {"image_id": statement_image_id}
                )

            df = self.get_data()
            df["StatementImageId"] = statement_image_id

            with get_connection("ldr") as conn:
                df.to_sql("ve_StatementStatementItem", conn, if_exists="append", index=False)

        except Exception as e:
            with get_connection("ldr") as conn:
                conn.execute(
                    text("UPDATE [Image] SET [ContentType]=:content_type, [StatusType]=:status_type WHERE [ImageId]=:image_id"),
                    {"image_id": statement_image_id, "content_type": self._image.ContentType, "status_type": self._image.StatusType}
                )
                conn.execute(text("DELETE FROM [Statement] WHERE [ImageId]=:image_id"), {"image_id": statement_image_id})

            messagebox.showerror("Error", "An error occurred while saving the statement. Please try again.", detail=str(e))
            os.startfile(self.temp_excel_tool_path)
            logger.error("An error occurred while saving the statement: %s", str(e))
