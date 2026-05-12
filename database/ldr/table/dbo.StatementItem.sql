CREATE TABLE [StatementItem] (
    [StatementId] UNIQUEIDENTIFIER NOT NULL,
    [StatementItemId] UNIQUEIDENTIFIER NOT NULL,
    [MethodId] UNIQUEIDENTIFIER NOT NULL,
    [PayeeId] UNIQUEIDENTIFIER NOT NULL,
    [InvoiceId] UNIQUEIDENTIFIER NULL,
    [TransactionDate] DATETIME2(0) NOT NULL,
    [PostDate] DATE NOT NULL,
    [ReferenceNumber] NVARCHAR(100) NULL,
    [Amount] DECIMAL(18, 2) NOT NULL,
    [Description] NVARCHAR(1000) NOT NULL,
    [ImageId] UNIQUEIDENTIFIER NULL,
    CONSTRAINT [PK_StatementItem] PRIMARY KEY NONCLUSTERED ([StatementItemId]),
    CONSTRAINT [FK_StatementItem_Method] FOREIGN KEY ([MethodId]) REFERENCES [Method]([MethodId]),
    CONSTRAINT [FK_StatementItem_Image] FOREIGN KEY ([ImageId]) REFERENCES [Image]([ImageId]) ON DELETE SET NULL,
    CONSTRAINT [FK_StatementItem_Statement] FOREIGN KEY ([StatementId]) REFERENCES [Statement]([StatementId]) ON DELETE CASCADE,
    CONSTRAINT [FK_StatementItem_Payee] FOREIGN KEY ([PayeeId]) REFERENCES [Payee]([PayeeId]),
    CONSTRAINT [FK_StatementItem_Invoice] FOREIGN KEY ([InvoiceId]) REFERENCES [Invoice]([InvoiceId]) ON DELETE SET NULL,
    CONSTRAINT [UQ_StatementItem] UNIQUE ([StatementId], [PayeeId], [TransactionDate], [Amount]),
    CONSTRAINT [CK_PostDate_After_TransactionDate] CHECK ([TransactionDate] <= DATEADD(SECOND, -1, DATEADD(DAY, 1, CAST([PostDate] AS DATETIME2(0))))));

CREATE CLUSTERED INDEX [IX_StatementItem] ON [StatementItem]([StatementId] ASC, [PostDate] ASC);