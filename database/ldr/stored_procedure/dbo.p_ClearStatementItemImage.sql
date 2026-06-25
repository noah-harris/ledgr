CREATE PROCEDURE p_ClearStatementItemImage (
	@StatementItemId UNIQUEIDENTIFIER
)
AS
BEGIN

	DECLARE @ImageId UNIQUEIDENTIFIER = (SELECT ImageId FROM StatementItem WHERE StatementItemId = @StatementItemId)

	UPDATE [StatementItem]
	SET [ImageId] = NULL
	WHERE [StatementItemId] = @StatementItemId

	UPDATE [ImageSort]
	SET 
		[StatusType] = 'u',
		[ContentType] = NULL
	WHERE [ImageId] = @ImageId

END
