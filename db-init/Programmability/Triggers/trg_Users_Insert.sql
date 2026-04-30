CREATE TRIGGER [trg_Users_Insert]
ON [Users]
AFTER INSERT
AS

BEGIN
    SET NOCOUNT ON
    SET XACT_ABORT ON

    BEGIN TRY
        BEGIN TRANSACTION

        INSERT INTO [Payee] ([PayeeId], [PayeeType])
        SELECT [UsersId], 'Users'
        FROM [inserted]

        COMMIT TRANSACTION
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION
        ;THROW
    END CATCH
END