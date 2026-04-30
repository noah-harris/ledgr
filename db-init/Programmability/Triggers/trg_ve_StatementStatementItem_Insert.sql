CREATE TRIGGER [trg_ve_StatementStatementItem_Insert]
ON [ve_StatementStatementItem]
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        DECLARE @StatementId UNIQUEIDENTIFIER = NEWID()

        INSERT INTO [Statement] ([AccountId], [StatementId], [StatementDate], [StartDate], [EndDate], [StartBalance], [EndBalance], [ImageId])
        SELECT DISTINCT
            i.[AccountId],
            ISNULL(i.[StatementId], @StatementId),
            i.[StatementDate],
            i.[StartDate],
            i.[EndDate],
            i.[StartBalance],
            i.[EndBalance],
            i.[StatementImageId]
        FROM [inserted] AS i


        INSERT INTO [StatementItem] ([StatementId], [StatementItemId], [MethodId], [PayeeId], [InvoiceId], [TransactionDate], [PostDate], [ReferenceNumber], [Amount], [Description], [ImageId])
        SELECT
            ISNULL(i.[StatementId], @StatementId),
            ISNULL(i.[StatementItemId], NEWID()),
            i.[MethodId],
            i.[PayeeId],
            i.[InvoiceId],
            i.[TransactionDate],
            i.[PostDate],
            i.[ReferenceNumber],
            i.[Amount],
            i.[Description],
            i.[StatementItemImageId]
        FROM [inserted] AS i

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;