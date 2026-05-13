CREATE TABLE [InvoiceItemCategory] (
    [CategoryId] UNIQUEIDENTIFIER NOT NULL,
    [Segment] NVARCHAR(50) NOT NULL,
    [Category] NVARCHAR(100) NOT NULL,
    [SubCategory] NVARCHAR(100) NOT NULL,
    [Unit] NVARCHAR(50) NOT NULL,
    [DisplayOrder] INT NOT NULL,
    [Description] NVARCHAR(255) NULL,
    CONSTRAINT [PK_InvoiceItemCategory] PRIMARY KEY CLUSTERED ([CategoryId])
)