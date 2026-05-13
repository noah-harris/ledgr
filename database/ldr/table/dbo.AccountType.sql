CREATE TABLE [AccountType] (
    [AccountTypeId] UNIQUEIDENTIFIER NOT NULL,
    [AccountTypeName] NVARCHAR(50) NOT NULL,
    [IsCredit] BIT NOT NULL DEFAULT 0,
    [Description] NVARCHAR(255) NULL,
    CONSTRAINT [PK_AccountType] PRIMARY KEY CLUSTERED ([AccountTypeId]),
    CONSTRAINT [UQ_AccountType_Name] UNIQUE ([AccountTypeName])
);