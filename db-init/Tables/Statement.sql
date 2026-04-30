CREATE TABLE [Statement] (
    [AccountId] UNIQUEIDENTIFIER NOT NULL,
    [StatementId] UNIQUEIDENTIFIER NOT NULL,
    [StatementDate] DATE NOT NULL,
    [StartDate] DATETIME2(0) NOT NULL,
    [EndDate] DATETIME2(0) NOT NULL,
    [StartBalance] DECIMAL(18, 2) NOT NULL,
    [EndBalance] DECIMAL(18, 2) NOT NULL,
    [ImageId] UNIQUEIDENTIFIER NULL,
    CONSTRAINT [PK_Statement] PRIMARY KEY NONCLUSTERED ([StatementId]),
    CONSTRAINT [FK_Statement_Account] FOREIGN KEY ([AccountId]) REFERENCES [Account]([AccountId]),
    CONSTRAINT [FK_Statement_Image] FOREIGN KEY ([ImageId]) REFERENCES [Image]([ImageId]) ON DELETE SET NULL
);

CREATE CLUSTERED INDEX [IX_Statement_Account] ON [Statement]([AccountId] ASC, [StatementDate] ASC);