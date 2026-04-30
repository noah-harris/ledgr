CREATE TABLE [Method] (
    [AccountId] UNIQUEIDENTIFIER NOT NULL,
    [MethodId] UNIQUEIDENTIFIER NOT NULL,
    [MethodTypeId] UNIQUEIDENTIFIER NOT NULL,
    [MethodNumber] NVARCHAR(50) NULL,
    [AmazonPaymentMethod] NVARCHAR(100) NULL,
    [ImageId] UNIQUEIDENTIFIER NULL,
    
    CONSTRAINT [PK_Method] PRIMARY KEY NONCLUSTERED ([MethodId]),
    CONSTRAINT [FK_Method_Account] FOREIGN KEY ([AccountId]) REFERENCES [Account]([AccountId]),
    CONSTRAINT [FK_Method_MethodType] FOREIGN KEY ([MethodTypeId]) REFERENCES [MethodType]([MethodTypeId]),
    CONSTRAINT [FK_Method_Image] FOREIGN KEY ([ImageId]) REFERENCES [Image]([ImageId]) ON DELETE SET NULL
);

CREATE CLUSTERED INDEX [IX_Method_Account_MethodType] ON [Method] ([AccountId], [MethodTypeId]);