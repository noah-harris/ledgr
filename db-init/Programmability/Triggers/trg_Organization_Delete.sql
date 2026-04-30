CREATE TRIGGER [trg_Organization_Delete]
ON [Organization]
INSTEAD OF DELETE
AS

BEGIN
    SET NOCOUNT ON
    SET XACT_ABORT ON

    BEGIN TRY
        BEGIN TRANSACTION

        DELETE FROM [Organization]
        WHERE [OrganizationId] IN (SELECT [OrganizationId] FROM [deleted])

        DELETE FROM [Payee]
        WHERE [PayeeId] IN (SELECT [OrganizationId] FROM [deleted])

        COMMIT TRANSACTION
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION
        ;THROW
    END CATCH
END