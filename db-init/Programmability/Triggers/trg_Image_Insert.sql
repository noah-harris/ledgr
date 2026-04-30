CREATE TRIGGER [trg_v_Image_Insert]
ON [v_Image]
INSTEAD OF INSERT
AS

BEGIN
    SET NOCOUNT ON
    SET XACT_ABORT ON

    BEGIN TRY
        BEGIN TRANSACTION

        DROP TABLE IF EXISTS #InsertedImages;
        SELECT 
            [UsersId],
            ISNULL([ImageId], CAST(HASHBYTES('MD5', CAST(LOWER([FileName] + '.' + [FileType]) AS NVARCHAR(861))) AS UNIQUEIDENTIFIER)) AS [ImageId],
            [FileName], 
            [FileType],
            [StatusType],
            [StatusName],
            [ContentType]
        INTO #InsertedImages
        FROM [inserted]

        INSERT INTO [Image] ([UsersId], [ImageId], [FileName], [FileType])
        SELECT [UsersId], [ImageId], [FileName], [FileType] FROM #InsertedImages

        INSERT INTO [ImageSort] ([ImageId], [StatusType], [ContentType])
        SELECT 
            [ImageId], 
            COALESCE(
                [StatusType], 
                (SELECT [StatusType] FROM [ImageSortStatusType] AS isst WHERE i.[StatusName] = isst.[StatusName]),
                'u' -- default to 'u' for unknown if no match is found
            ) AS [StatusType], 
            [ContentType]
        FROM #InsertedImages AS i

        COMMIT TRANSACTION
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION
        ;THROW
    END CATCH
END