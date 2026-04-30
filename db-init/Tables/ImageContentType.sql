CREATE TABLE [ImageContentType] (
    [ContentType] VARCHAR(50) NOT NULL,
    [Description] NVARCHAR(255) NOT NULL,
    CONSTRAINT [PK_ImageContentType] PRIMARY KEY CLUSTERED ([ContentType])
);