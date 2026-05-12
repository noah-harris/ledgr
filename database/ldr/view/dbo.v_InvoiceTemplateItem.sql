CREATE VIEW [v_InvoiceTemplateItem]
    AS
SELECT
    it.[InvoiceTemplateId],
    it.[InvoiceTemplateName],
    iit.[InvoiceTemplateItemId],
    iit.[CategoryId],
    iic.[CategoryDisplayName],
    iit.[Description],
    iit.[Quantity],
    iit.[Amount],
    iit.[DisplayOrder]
FROM [InvoiceTemplateItem] AS iit
JOIN [v_InvoiceTemplate] AS it ON it.[InvoiceTemplateId] = iit.[InvoiceTemplateId]
JOIN [v_InvoiceItemCategory] AS iic ON iic.[CategoryId] = iit.[CategoryId]
