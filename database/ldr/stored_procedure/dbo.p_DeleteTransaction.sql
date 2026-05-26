
CREATE PROCEDURE [dbo].[p_DeleteTransaction] (
    @StatementItemId UNIQUEIDENTIFIER
)
	AS
SET NOCOUNT ON;

DECLARE @InvoiceId UNIQUEIDENTIFIER
DECLARE @StatementItemIds TABLE ([StatementItemId] UNIQUEIDENTIFIER)
DECLARE @ImageIds TABLE ([ImageId] UNIQUEIDENTIFIER)


BEGIN
	BEGIN TRY
        BEGIN TRANSACTION


            -- Get Invoice Id
            SET @InvoiceId = (SELECT [InvoiceId] FROM [StatementItem] AS si WHERE si.[StatementItemId] = @StatementItemId)


            -- Get StatementItem Ids
            INSERT INTO @StatementItemIds VALUES (@StatementItemId)
            INSERT INTO @StatementItemIds SELECT [StatementItemId] FROM [StatementItem] WHERE [InvoiceId] = @InvoiceId

            
            -- Get ImageIds
            INSERT INTO @ImageIds SELECT [ImageId] FROM [Invoice] WHERE [InvoiceId] = @InvoiceId
            INSERT INTO @ImageIds SELECT [ImageId] FROM [StatementItem] WHERE [StatementItemId] IN (SELECT [StatementItemId] FROM @StatementItemIds)


            -- Reset StatementItem
            UPDATE si
            SET 
                si.[InvoiceId] = NULL,
                si.[ImageId] = NULL
            FROM [StatementItem] AS si
            WHERE EXISTS (
                SELECT NULL
                FROM @ImageIds AS id
                WHERE id.[ImageId] = si.[ImageId]
            )

            -- Reset Image
            UPDATE s
            SET 
                s.[StatusType] = 'u',
                s.[ContentType] = NULL
            FROM [ImageSort] AS s
            WHERE EXISTS (
                SELECT NULL
                FROM @ImageIds AS i
                WHERE i.[ImageId] = s.[ImageId]
            )

            -- Delete Invoice
            DELETE FROM [Invoice] WHERE [InvoiceId] = @InvoiceId

        COMMIT TRANSACTION
	END TRY

    BEGIN CATCH 
      IF (@@TRANCOUNT > 0)
       BEGIN
          ROLLBACK TRANSACTION SCHEDULEDELETE
          PRINT 'Error detected, all changes reversed'
       END 
        SELECT
            ERROR_NUMBER() AS ErrorNumber,
            ERROR_SEVERITY() AS ErrorSeverity,
            ERROR_STATE() AS ErrorState,
            ERROR_PROCEDURE() AS ErrorProcedure,
            ERROR_LINE() AS ErrorLine,
            ERROR_MESSAGE() AS ErrorMessage
    END CATCH

END