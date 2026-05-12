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

        /* 
        Custom error handling for duplicate filenames 
        Check for duplicate filenames (case-insensitive)
        */
        
        DECLARE @DuplicateName NVARCHAR(512)
        SELECT TOP 1 @DuplicateName = i.[FileName] + '.' + i.[FileType]
        FROM #InsertedImages AS i
        INNER JOIN [Image] AS existing
            ON existing.[ImageId] = i.[ImageId]

        IF @DuplicateName IS NOT NULL
        BEGIN
            DECLARE @ErrMsg NVARCHAR(1000) = 
                'An image named "' + @DuplicateName + '" has already been uploaded.'
            ;THROW 51000, @ErrMsg, 1
        END


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