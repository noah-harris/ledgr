CREATE VIEW [dbo].[v_Invoice]
	AS 
SELECT 
	i.[InvoiceId],
	p.[PayeeId],  
	p.[PayeeName],
	p.[PayeeType],
	i.[InvoiceDate],
	i.[DueDate],
	i.[InvoiceNumber],
	i.[Amount],
	i.[Description],
	i.[StartDate],
	i.[EndDate],
	img.[ImageId], 
	img.[ImageFileName]
FROM [Invoice] AS i
LEFT JOIN [v_Image] AS img ON img.[ImageId] = i.[ImageId]
JOIN [v_Payee] AS p ON i.[PayeeId] = p.[PayeeId]