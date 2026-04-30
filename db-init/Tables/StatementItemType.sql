CREATE TABLE [StatementItemType] (
    [StatementItemTypeId] UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    [StatementItemTypeName] NVARCHAR(255) NOT NULL,
    [Description] NVARCHAR(1000) NULL
)