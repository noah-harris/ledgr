from db import get_connection
from functools import cache
import pandas as pd
from sqlalchemy import engine, text
from tkinter import messagebox

# THis temp
def get_payee_id(name:str) -> str | None:
    with get_connection() as conn:
        df = pd.read_sql_query(text("SELECT [PayeeId] FROM [v_Payee] WHERE [PayeeName] = :name"), conn, params={"name": name})
        return df["PayeeId"].iloc[0] if not df.empty else None
    

def get_category_id(name:str) -> str | None:
    with get_connection() as conn:
        df = pd.read_sql_query(text("SELECT [CategoryId] FROM [v_InvoiceItemCategory] WHERE [CategoryDisplayName] = :name"), conn, params={"name": name})
        return df["CategoryId"].iloc[0] if not df.empty else None


# SELECT DATA
def Invoice() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [Invoice]", conn)

def InvoiceItem() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [InvoiceItem]", conn)

def Account() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [v_Account]", conn)

def Payee() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [v_Payee] ORDER BY [PayeeType], [PayeeName]", conn)
    
def v_Method() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [v_Method] ORDER BY [MethodTypeName], [MethodDisplayName]", conn)
    
def Users() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [v_Users]", conn)
    
def AccountType() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [AccountType]", conn)

def BankOrganization() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [v_Organization] WHERE [IsAccountProvider] = 1", conn)

def InvoiceItemCategory() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [v_InvoiceItemCategory]", conn)
    
def Statement() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [v_Statement]", conn)

def v_StatementItem() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("""
        SELECT 
            [AccountDisplayName] AS [Account],
            [StatementDate],
            [TransactionDate],
            [PostDate],
            [ReferenceNumber],
            [Description],
            [Amount],
            [PayeeName] AS [Payee],
            [MethodDisplayName] AS [Method],
            [StatementItemId],
            [ImageId],
            [InvoiceId],
            [StatementId]
        FROM [v_StatementItem]
    """, conn)

def UnmatchedImages() -> pd.DataFrame:
    with get_connection() as conn:
        queue:pd.DataFrame = pd.read_sql_query("""
            SELECT 
                [ImageId],
                [FileName],
                [FileType],
                [StatusType],
                [StatusName],
                [ContentType],
                [ImageFileName]
            FROM [v_Image] 
            WHERE [StatusType] ='u'
        """, conn)
    return queue

def InvoiceTemplates() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [v_InvoiceTemplate]", conn)
    
def ImageContentType() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [ImageContentType]", conn)
    
def v_Invoice() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [v_Invoice]", conn)

def v_Image() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("""
            SELECT
                [ImageId],
                [FileName],
                [FileType],
                [StatusType],
                [StatusName],
                [ContentType],
                [ImageFileName]
            FROM [v_Image]
        """, conn)
    

# Display
def v_DisplayInvoice() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [v_DisplayInvoice]", conn)
    
def v_DisplayInvoiceItem() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [v_DisplayInvoiceItem]", conn)
    
def v_DisplayStatementItem() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM [v_DisplayStatementItem]", conn)
    


# Utility functions
def v_StatementItemUnmatchedImages() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("""
        SELECT 
            si.[AccountDisplayName] AS [Account],
            si.[StatementDate],
            si.[TransactionDate],
            si.[PostDate],
            si.[ReferenceNumber],
            si.[Description],
            si.[Amount] AS [Amount],
            si.[PayeeName] AS [Payee],
            si.[MethodDisplayName] AS [Method],
            si.[StatementItemId],
            si.[ImageId],
            si.[InvoiceId],
            si.[StatementId]
        FROM [v_StatementItem] AS si
        JOIN [Account] AS a ON a.[AccountId] = si.[AccountId]
        JOIN [Currency] AS c ON c.[Currency] = a.[Currency]
        WHERE [ImageId] IS NULL
    """, conn)

# Utility functions
def v_StatementItemAccountTransfer() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("""
            SELECT
                si.[AccountDisplayName] AS [Account],
                si.[StatementDate],
                si.[TransactionDate],
                si.[PostDate],
                si.[PayeeName] AS [Payee],
                si.[ReferenceNumber],
                si.[Description],
                si.[Amount],
                si.[MethodDisplayName] AS [Method],
                si.[StatementItemId],
                si.[PayeeId]
            FROM [v_StatementItem] AS si
            WHERE 1=1 
                AND [PayeeType] = 'Account'
                AND [InvoiceId] IS NULL 
                AND [ImageId] IS NULL
    """, conn)
    
def v_StatementItemLinkable() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("""
            SELECT
                si.[AccountDisplayName] AS [Account],
                si.[StatementDate],
                si.[TransactionDate],
                si.[PostDate],
                si.[PayeeName] AS [Payee],
                si.[ReferenceNumber],
                si.[Description],
                si.[Amount],
                si.[MethodDisplayName] AS [Method],
                si.[StatementItemId],
                si.[PayeeId]
            FROM [v_StatementItem] AS si
            WHERE 1=1 
                AND [ContentType] IN ('RECEIPT', 'TRANSACTION')
                AND [InvoiceId] IS NULL
    """, conn)


# UPDATE FUNCTIONS
def update_image_sort(conn:engine.Connection, image_id, content_type, status_type):
    try:
        query = text("UPDATE [ImageSort] SET [StatusType]=:status_type, [ContentType]=:content_type WHERE [ImageId]=:image_id")
        params = {"image_id": image_id, "content_type": content_type, "status_type": status_type}
        conn.execute(query, params)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to Update Image Info: {str(e)}")
        raise e
    
def update_image_sort_status(conn:engine.Connection, image_id, status_type):
    try:
        query = text("UPDATE [ImageSort] SET [StatusType]=:status_type  WHERE [ImageId]=:image_id")
        params = {"image_id": image_id, "status_type": status_type}
        conn.execute(query, params)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to Update Image Info: {str(e)}")
        raise e

def update_statement_item_image_id(conn:engine.Connection, image_id, statement_item_id):
    try:
        query = text("UPDATE [StatementItem] SET [ImageId]=:image_id WHERE [StatementItemId]=:statement_item_id")
        params = {"image_id": image_id, "statement_item_id": statement_item_id}
        conn.execute(query, params)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to Update Statement Item ImageId: {str(e)}")
        raise e

def update_statement_item_invoice_id(conn:engine.Connection, invoice_id, statement_item_id):
    try:
        query = text("UPDATE [StatementItem] SET [InvoiceId]=:invoice_id WHERE [StatementItemId]=:statement_item_id")
        params = {"invoice_id": invoice_id, "statement_item_id": statement_item_id}
        conn.execute(query, params)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to Update Statement Item InvoiceId: {str(e)}")
        raise e

# INSERT FUNCTIONS

def insert_invoice(conn:engine.Connection, invoice:dict, invoice_item:pd.DataFrame):
    invoice_df = pd.DataFrame([invoice])
    try:
        invoice_df.to_sql("Invoice", conn, if_exists="append", index=False)
        invoice_item.to_sql("InvoiceItem", conn, if_exists="append", index=False)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to Insert Invoice: {str(e)}")
        raise e
    






