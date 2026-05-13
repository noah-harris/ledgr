CREATE VIEW [v_StatementItem]
	AS
SELECT
	vs.[AccountId], 
	vs.[StatementId], 
	si.[StatementItemId], 
	vi.[InvoiceId],
	vp.[PayeeId], 
	vm.[MethodId],
    vs.[AccountDisplayName],
	vs.[StatementDate], 
	vi.[InvoiceDate], vi.[DueDate], vi.[InvoiceNumber], vi.[Amount] AS [InvoiceAmount], vi.[Description] AS [InvoiceDescription], vi.[StartDate], vi.[EndDate],
	vm.[MethodDisplayName],
	vm.[IsAccountTransferMethod],
	vp.[PayeeName],
	vp.[PayeeType],
	si.[TransactionDate],
	si.[PostDate],
	si.[ReferenceNumber],
	si.[Description],
	si.[Amount],
	vimg.[ImageId],
	vimg.[ImageFileName],
	vimg.[ContentType],
	vimg.[StatusType]
FROM [StatementItem] AS si
JOIN [v_Statement] AS vs ON si.[StatementId] = vs.[StatementId]
JOIN [v_Account] AS va ON vs.[AccountId] = va.[AccountId]
JOIN [v_Payee] AS vp ON si.[PayeeId] = vp.[PayeeId]
JOIN [v_Method] AS vm ON si.[MethodId] = vm.[MethodId]
LEFT JOIN [v_Image] AS vimg ON si.[ImageId] = vimg.[ImageId]
LEFT JOIN [v_Invoice] AS vi ON si.[InvoiceId] = vi.[InvoiceId]