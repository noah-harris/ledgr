CREATE PROCEDURE [check].[p_TransactionAmounts]
    AS
    SET NOCOUNT ON;
BEGIN
    ; 
    WITH CTE_InvoiceItems AS (
        SELECT 
            InvoiceId, 
            SUM(Amount) AS Amount
        FROM InvoiceItem 
        GROUP BY InvoiceId
    ),
    CTE_StatementItem AS (
        SELECT 
            InvoiceId, 
            SUM(Amount) AS Amount 
        FROM StatementItem 
        GROUP BY InvoiceId
    )
    SELECT i.InvoiceId, i.Amount AS [InvoiceAmount], ii.[Amount] AS [InvoiceItemAmount], si.[Amount] AS [StatementItemAmount]
    FROM Invoice AS i
    JOIN CTE_InvoiceItems AS ii ON i.InvoiceId = ii.InvoiceId
    JOIN CTE_StatementItem AS si ON i.InvoiceId = si.InvoiceId
    WHERE 1=2
        OR i.[Amount] <> si.[Amount]
        OR i.[Amount] <> ii.[Amount]
        OR ii.Amount <> si.Amount
END