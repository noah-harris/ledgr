CREATE TRIGGER [trg_Organization_Insert]
ON [Organization]
AFTER INSERT
AS

BEGIN
    SET NOCOUNT ON
    SET XACT_ABORT ON

    BEGIN TRY
        BEGIN TRANSACTION

        INSERT INTO [Payee] ([PayeeId], [PayeeType])
        SELECT [OrganizationId], 'Organization'
        FROM [inserted]

        COMMIT TRANSACTION
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION
        ;THROW
    END CATCH
END