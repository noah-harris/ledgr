CREATE PROCEDURE p_ClearInvoiceImage (
	@InvoiceId UNIQUEIDENTIFIER
)
AS
BEGIN

	DECLARE @ImageId UNIQUEIDENTIFIER = (SELECT ImageId FROM Invoice WHERE InvoiceId = @InvoiceId)

	UPDATE [Invoice]
	SET [ImageId] = NULL
	WHERE [InvoiceId] = @InvoiceId

	UPDATE [ImageSort]
	SET 
		[StatusType] = 'u',
		[ContentType] = NULL
	WHERE [ImageId] = @ImageId

END