CREATE TRIGGER [trg_StatementItem_Validation]
ON [StatementItem]
AFTER INSERT,UPDATE
AS

BEGIN
    SET NOCOUNT ON

    -- Check that PayeeId on StatementItem matches PayeeId on related Invoice
    IF EXISTS (
        SELECT NULL
        FROM [inserted] AS i
        JOIN [Invoice] AS inv ON i.[InvoiceId] = inv.[InvoiceId]
        WHERE i.[PayeeId] <> inv.[PayeeId]
    )
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 51000, 'PayeeId on StatementItem must match PayeeId on related Invoice.', 1;
    END

    -- Check that TransactionDate on StatementItem is not earlier than InvoiceDate on related Invoice
    IF EXISTS (
        SELECT NULL
        FROM [inserted] AS i
        JOIN [Invoice] AS inv ON i.[InvoiceId] = inv.[InvoiceId]
        WHERE i.[TransactionDate] < inv.[InvoiceDate]
    )
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 51000, 'TransactionDate on StatementItem cannot be earlier than InvoiceDate on related Invoice.', 1;
    END

    -- Check that PostDate on StatementItem is not earlier than InvoiceDate on related Invoice
    IF EXISTS (
        SELECT NULL
        FROM [inserted] AS i
        JOIN [Invoice] AS inv ON i.[InvoiceId] = inv.[InvoiceId]
        WHERE CAST(i.[PostDate] AS DATE) < CAST(inv.[InvoiceDate] AS DATE)
    )
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 51000, 'PostDate on StatementItem cannot be earlier than InvoiceDate on related Invoice.', 1;
    END

    -- Check that Amount on StatementItem matches BalanceChange on related Statementq
    IF EXISTS (
        SELECT NULL
        FROM [inserted] AS i
        GROUP BY [StatementItemId]
        HAVING SUM([Amount]) <> (SELECT [vs.[BalanceChange] FROM [dbo].[v_Statement] AS vs WHERE vs.[StatementId] = i.[StatementId])
    )
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 51000, 'Amount on StatementItem must match BalanceChange on related Statement.', 1;
    END


END