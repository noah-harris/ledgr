CREATE TABLE [ImageSort] (
    [ImageId] UNIQUEIDENTIFIER NOT NULL,
    [StatusType] CHAR(1) NOT NULL DEFAULT 'u',
    [ContentType] VARCHAR(50) NULL,
    CONSTRAINT [PK_ImageSort] PRIMARY KEY CLUSTERED ([ImageId]),
    CONSTRAINT [FK_ImageSort_Image] FOREIGN KEY ([ImageId]) REFERENCES [Image]([ImageId]) ON DELETE CASCADE,
    CONSTRAINT [FK_ImageSort_ImageSortStatus] FOREIGN KEY ([StatusType]) REFERENCES [ImageSortStatusType]([StatusType]) ON DELETE NO ACTION,
    CONSTRAINT [FK_ImageSort_ContentType] FOREIGN KEY ([ContentType]) REFERENCES [ImageContentType]([ContentType]) ON DELETE NO ACTION
);