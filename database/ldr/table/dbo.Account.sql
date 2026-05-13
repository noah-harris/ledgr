CREATE TABLE [Account] (
    [UsersId] UNIQUEIDENTIFIER NOT NULL,
    [AccountId] UNIQUEIDENTIFIER NOT NULL,
    [AccountTypeId] UNIQUEIDENTIFIER NOT NULL,
    [OrganizationId] UNIQUEIDENTIFIER NOT NULL,
    [AccountNumber] NVARCHAR(50) NOT NULL,
    [Currency] NVARCHAR(3) NOT NULL,
    [Description] NVARCHAR(255) NULL,
    [StartDate] DATETIME2(0) NOT NULL DEFAULT '2000-01-01 00:00:00',
    [EndDate] DATETIME2(0) NOT NULL DEFAULT '2050-12-31 23:59:59',
    CONSTRAINT [PK_Account] PRIMARY KEY NONCLUSTERED ([AccountId]),
    CONSTRAINT [FK_Account_Users] FOREIGN KEY ([UsersId]) REFERENCES [Users]([UsersId]),
    CONSTRAINT [FK_Account_Organization] FOREIGN KEY ([OrganizationId]) REFERENCES [Organization]([OrganizationId]),
    CONSTRAINT [FK_Account_AccountType] FOREIGN KEY ([AccountTypeId]) REFERENCES [AccountType]([AccountTypeId]),
    CONSTRAINT [FK_Account_Currency] FOREIGN KEY ([Currency]) REFERENCES [Currency]([Currency])
);

CREATE CLUSTERED INDEX [IX_Account_Users_Organization_AccountType] ON [Account] ([UsersId], [OrganizationId], [AccountTypeId]);