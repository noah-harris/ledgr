CREATE VIEW [v_InvoiceTemplate]
    AS
SELECT
    it.[InvoiceTemplateId],
    it.[InvoiceTemplateName],
    it.[PayeeId],
    p.[PayeeName]
FROM [InvoiceTemplate] AS it
LEFT JOIN [v_Payee] AS p ON p.[PayeeId] = it.[PayeeId]