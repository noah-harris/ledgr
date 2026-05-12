CREATE TABLE [ImageSortStatusType] (
    [StatusType] CHAR(1) NOT NULL,
    [StatusName] VARCHAR(50) NOT NULL,
    [Description] NVARCHAR(255) NOT NULL,
    CONSTRAINT [PK_ImageSortStatusType] PRIMARY KEY CLUSTERED ([StatusType])
);