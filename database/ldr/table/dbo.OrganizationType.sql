CREATE TABLE [OrganizationType] (
    [OrganizationTypeId] UNIQUEIDENTIFIER NOT NULL,
    [OrganizationTypeName] NVARCHAR(100) NOT NULL,
    [IsAccountProvider] BIT NOT NULL,
    [Segment] NVARCHAR(50) NOT NULL,
    [Description] NVARCHAR(255) NOT NULL,
    CONSTRAINT [PK_OrganizationType] PRIMARY KEY CLUSTERED ([OrganizationTypeId])
);