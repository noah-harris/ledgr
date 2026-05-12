CREATE TABLE [InvoiceTemplate]
(
    [InvoiceTemplateId] UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    [InvoiceTemplateName] NVARCHAR(100) NOT NULL,
    CONSTRAINT [UQ_InvoiceTemplateName] UNIQUE ([InvoiceTemplateName])
)