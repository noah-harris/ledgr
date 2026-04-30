CREATE TABLE [InvoiceTemplateItem]
(
    [InvoiceTemplateId] UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID(),
    [InvoiceTemplateItemId] UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID(),
    [CategoryId] UNIQUEIDENTIFIER NOT NULL,
    [Description] NVARCHAR(255) NOT NULL,
    [Quantity] DECIMAL(10, 3) NULL,
    [Amount] DECIMAL(20, 2) NULL,
    [DisplayOrder] INT NOT NULL,
    CONSTRAINT [PK_InvoiceTemplateItem] PRIMARY KEY NONCLUSTERED ([InvoiceTemplateId], [InvoiceTemplateItemId]),
    CONSTRAINT [FK_InvoiceTemplateItem_InvoiceTemplate] FOREIGN KEY ([InvoiceTemplateId]) REFERENCES [InvoiceTemplate]([InvoiceTemplateId]),
    CONSTRAINT [FK_InvoiceTemplateItem_Category] FOREIGN KEY ([CategoryId]) REFERENCES [InvoiceItemCategory]([CategoryId])
)