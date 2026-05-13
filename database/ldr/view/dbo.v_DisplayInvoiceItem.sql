CREATE VIEW [v_DisplayInvoiceItem] AS
SELECT 
    [InvoiceId],
	[DisplayOrder] AS [#],
	[CategoryDisplayName] AS [Category],
	[Quantity] AS [Qty],
	'$'+CAST([Amount] AS VARCHAR(50))AS [Amt],
	UPPER([Description]) AS [Description]
FROM [v_InvoiceItem] AS ii
