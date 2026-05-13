CREATE VIEW [v_DisplayInvoice] AS
SELECT
    i.[InvoiceId],
	p.[PayeeName],
	p.[PayeeType],
	p.[Description] AS [PayeeDescription],
	i.[InvoiceDate],
	i.[DueDate],
	i.[InvoiceNumber],
	i.[Amount],
	i.[Description] AS [InvoiceDescription],
	i.[StartDate],
	i.[EndDate],
	vi.[ImageFileName]
FROM [Invoice] AS i
JOIN [v_Payee] AS p ON i.[PayeeId] = p.[PayeeId]
LEFT JOIN [v_Image] AS vi ON vi.[ImageId] = i.[ImageId]
