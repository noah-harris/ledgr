CREATE TRIGGER [trg_Users_Delete]
ON [Users]
INSTEAD OF DELETE
AS

BEGIN
    SET NOCOUNT ON
    SET XACT_ABORT ON

    BEGIN TRY
        BEGIN TRANSACTION

        DELETE FROM [Users]
        WHERE [UsersId] IN (SELECT [UsersId] FROM [deleted])

        DELETE FROM [UsersGroupMember]
        WHERE [UsersId] IN (SELECT [UsersId] FROM [deleted])

        DELETE FROM [Payee]
        WHERE [PayeeId] IN (SELECT [UsersId] FROM [deleted])

        COMMIT TRANSACTION
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION
        ;THROW
    END CATCH
END