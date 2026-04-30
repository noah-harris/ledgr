CREATE TABLE [AccountTypeMethodTypeTemplate] (
    [AccountTypeId] UNIQUEIDENTIFIER NOT NULL,
    [MethodTypeId] UNIQUEIDENTIFIER NOT NULL,
    [DefaultMethodName] NVARCHAR(100) NOT NULL,
    [IsAccountTransferMethod] BIT NOT NULL,
    CONSTRAINT [PK_AccountTypeMethodTypeTemplate] PRIMARY KEY CLUSTERED ([AccountTypeId], [MethodTypeId]),
    CONSTRAINT [FK_AccountTypeMethodTypeTemplate_AccountType] FOREIGN KEY ([AccountTypeId]) REFERENCES [AccountType]([AccountTypeId]),
    CONSTRAINT [FK_AccountTypeMethodTypeTemplate_MethodType] FOREIGN KEY ([MethodTypeId]) REFERENCES [MethodType]([MethodTypeId])
);

