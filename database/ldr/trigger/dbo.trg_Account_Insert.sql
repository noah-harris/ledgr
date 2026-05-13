CREATE TRIGGER [trg_Account_Insert]
ON [Account]
AFTER INSERT
AS

BEGIN
    SET NOCOUNT ON
    SET XACT_ABORT ON

    BEGIN TRY
        BEGIN TRANSACTION

        INSERT INTO [Payee] ([PayeeId], [PayeeType])
        SELECT [AccountId], 'Account'
        FROM [inserted]

        COMMIT TRANSACTION
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION
        ;THROW
    END CATCH
END