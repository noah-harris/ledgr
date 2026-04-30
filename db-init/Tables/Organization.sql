CREATE TABLE [Organization] (
    [OrganizationId] UNIQUEIDENTIFIER NOT NULL,
    [OrganizationName] NVARCHAR(100) NOT NULL,
    [OrganizationTypeId] UNIQUEIDENTIFIER NOT NULL,
    [Description] NVARCHAR(255) NULL,
    CONSTRAINT [PK_Organization] PRIMARY KEY NONCLUSTERED ([OrganizationId]),
    CONSTRAINT [FK_Organization_OrganizationType] FOREIGN KEY ([OrganizationTypeId]) REFERENCES [OrganizationType]([OrganizationTypeId])
);
CREATE CLUSTERED INDEX [IX_Organization_OrganizationType] ON [Organization] ([OrganizationTypeId]);