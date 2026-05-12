CREATE TRIGGER [trg_Account_Delete]
ON [Account]
INSTEAD OF DELETE
AS

BEGIN
    SET NOCOUNT ON
    SET XACT_ABORT ON

    BEGIN TRY
        BEGIN TRANSACTION

        DELETE FROM [Account]
        WHERE [AccountId] IN (SELECT [AccountId] FROM [deleted])

        DELETE FROM [Payee]
        WHERE [PayeeId] IN (SELECT [AccountId] FROM [deleted])

        COMMIT TRANSACTION
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION
        ;THROW
    END CATCH
END