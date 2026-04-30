CREATE VIEW [ve_StatementStatementItem]
    AS
SELECT
    -- Statement columns
    s.[AccountId],
    s.[StatementId],
    s.[StatementDate],
    s.[StartDate],
    s.[EndDate],
    s.[StartBalance],
    s.[EndBalance],
    s.[ImageId] AS [StatementImageId],

    -- StatementItem columns
    si.[StatementItemId],
    si.[MethodId],
    si.[PayeeId],
    si.[InvoiceId],
    si.[TransactionDate],
    si.[PostDate],
    si.[ReferenceNumber],
    si.[Amount],
    si.[Description],
    si.[ImageId] AS [StatementItemImageId]
FROM [Statement] AS s
LEFT JOIN [StatementItem] AS si ON si.[StatementId] = s.[StatementId]
