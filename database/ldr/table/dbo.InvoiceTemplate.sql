CREATE TABLE [InvoiceTemplate]
(
    [InvoiceTemplateId] UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    [InvoiceTemplateName] NVARCHAR(100) NOT NULL,
    [PayeeId] UNIQUEIDENTIFIER NULL,
    CONSTRAINT [UQ_InvoiceTemplateName] UNIQUE ([InvoiceTemplateName])
)