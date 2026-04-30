CREATE TABLE [MethodType] (
    [MethodTypeId] UNIQUEIDENTIFIER NOT NULL,
    [MethodTypeName] NVARCHAR(50) NOT NULL,
    [Description] NVARCHAR(255) NULL,
    CONSTRAINT [PK_MethodType] PRIMARY KEY CLUSTERED ([MethodTypeId]),
    CONSTRAINT [UQ_MethodType_Name] UNIQUE ([MethodTypeName])
);