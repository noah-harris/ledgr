CREATE VIEW [v_InvoiceItem]
    AS
SELECT 
	ii.[InvoiceId],
	ii.[InvoiceItemId],
	ii.[CategoryId], iic.[Segment], iic.[Category], iic.[Subcategory], iic.[CategoryDisplayName],
	ii.[Quantity],
	iic.[Unit],
	ii.[Amount],
	ii.[Description],
	ii.[DisplayOrder]
FROM [InvoiceItem] AS ii
JOIN [v_Invoice] AS vi ON vi.[InvoiceId] = ii.[InvoiceId]
JOIN [v_InvoiceItemCategory] AS iic ON ii.[CategoryId] = iic.[CategoryId]

