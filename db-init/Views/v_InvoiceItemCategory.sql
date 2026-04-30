CREATE VIEW [dbo].[v_InvoiceItemCategory]
    AS
SELECT 
    [CategoryId],
    [Segment],
    [Category],
    [Subcategory],
    [Segment] + ' - ' + [Category] + ' - ' + [Subcategory] AS [CategoryDisplayName],
    [Unit],
    [DisplayOrder]
FROM [InvoiceItemCategory]