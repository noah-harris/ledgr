from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import pandas as pd
from sqlalchemy import text
import data
from db import get_connection
from .StatementItem import StatementItem

@dataclass
class Invoice:
    InvoiceId: str
    PayeeName: str = None
    PayeeType: str = None
    PayeeDescription: str = None
    InvoiceDate: datetime = None
    DueDate: datetime = None
    InvoiceNumber: str = None
    Amount: Decimal = None
    InvoiceDescription: str = None
    StartDate: datetime = None
    EndDate: datetime = None
    ImageFileName: str = None
    ImageId: str = None
    InvoiceItems: pd.DataFrame = None
    StatementItems: list[str] = None

    def __post_init__(self):
        self.InvoiceItems = pd.DataFrame(columns=["InvoiceId", "#", "Category", "Qty", "Amt", "Description"])
        self.StatementItems = []
        df = data.v_DisplayInvoice()
        df = df[df['InvoiceId'] == str(self.InvoiceId).upper()]

        if not df.empty:
            self.PayeeName = df.iloc[0]['PayeeName']
            self.PayeeType = df.iloc[0]['PayeeType']
            self.PayeeDescription = df.iloc[0]['PayeeDescription']
            self.InvoiceDate = df.iloc[0]['InvoiceDate']
            self.DueDate = df.iloc[0]['DueDate']
            self.InvoiceNumber = df.iloc[0]['InvoiceNumber']
            self.Amount = round(Decimal(df.iloc[0]['Amount']), 2) if df.iloc[0]['Amount'] is not None else None
            self.InvoiceDescription = df.iloc[0]['InvoiceDescription']
            self.StartDate = df.iloc[0]['StartDate']
            self.EndDate = df.iloc[0]['EndDate']
            self.ImageFileName = df.iloc[0]['ImageFileName']

            with get_connection("ldr") as conn:
                row = conn.execute(
                    text("SELECT [ImageId] FROM [Invoice] WHERE [InvoiceId]=:id"),
                    {"id": str(self.InvoiceId).upper()}
                ).fetchone()
                self.ImageId = str(row[0]).upper() if row and row[0] else None

            invoice_item = data.v_DisplayInvoiceItem()
            self.InvoiceItems = invoice_item[invoice_item['InvoiceId'] == str(self.InvoiceId).upper()].sort_values("#")

            df = data.v_DisplayStatementItem()
            df = df[df['InvoiceId'] == str(self.InvoiceId).upper()]

            for _, row in df.iterrows():
                statement_item = StatementItem(StatementItemId=row['StatementItemId'])
                self.StatementItems.append(statement_item)
        else:
            self.InvoiceId = None