from dataclasses import dataclass
from datetime import datetime
import data

@dataclass
class StatementItem:
    StatementItemId: str
    PayeeName: str = None
    PayeeType: str = None
    PayeeDescription: str = None
    TransactionDate: datetime = None
    PostDate: datetime = None
    ReferenceNumber: str = None
    Amount: float = None
    StatementItemDescription: str = None
    AccountOrganizationName: str = None
    AccountOrganizationTypeName: str = None
    AccountNumber: str = None
    AccountDescription: str = None
    AccountStartDate: str = None
    AccountEndDate: str = None
    AccountTypeName: str = None
    Currency: str = None
    CurrencySymbol: str = None
    MethodNumber: str = None
    MethodTypeName: str = None
    MethodDescription: str = None
    PaymentDisplayNumber: str = None
    ImageFileName: str = None
    ImageContentType:str = None
    InvoiceId: str = None
    ImageId:str = None

    def __post_init__(self):
        df = data.v_DisplayStatementItem()
        df = df[df['StatementItemId'] == str(self.StatementItemId).upper()]

        if not df.empty:
            self.PayeeName = df.iloc[0]['PayeeName']
            self.PayeeType = df.iloc[0]['PayeeType']
            self.PayeeDescription = df.iloc[0]['PayeeDescription']
            self.TransactionDate = df.iloc[0]['TransactionDate']
            self.PostDate = df.iloc[0]['PostDate']
            self.ReferenceNumber = df.iloc[0]['ReferenceNumber']
            self.Amount = df.iloc[0]['Amount']
            self.StatementItemDescription = df.iloc[0]['StatementItemDescription']
            self.AccountOrganizationName = df.iloc[0]['AccountOrganizationName']
            self.AccountOrganizationTypeName = df.iloc[0]['AccountOrganizationTypeName']
            self.AccountNumber = df.iloc[0]['AccountNumber']
            self.AccountDescription = df.iloc[0]['AccountDescription']
            self.AccountStartDate = df.iloc[0]['AccountStartDate']
            self.AccountEndDate = df.iloc[0]['AccountEndDate']
            self.AccountTypeName = df.iloc[0]['AccountTypeName']
            self.Currency = df.iloc[0]['Currency']
            self.CurrencySymbol = df.iloc[0]['CurrencySymbol']
            self.MethodNumber = df.iloc[0]['MethodNumber']
            self.MethodTypeName = df.iloc[0]['MethodTypeName']
            self.MethodDescription = df.iloc[0]['MethodDescription']
            self.PaymentDisplayNumber = df.iloc[0]['PaymentDisplayNumber']
            self.ImageFileName = df.iloc[0]['ImageFileName']
            self.ImageContentType = df.iloc[0]['ImageContentType']
            self.InvoiceId = str(df.iloc[0]['InvoiceId']).upper() if df.iloc[0]['InvoiceId'] else None
            self.ImageId = str(df.iloc[0]['ImageId']).upper() if df.iloc[0]['ImageId'] else None
        else:
            self.StatementItemId = None