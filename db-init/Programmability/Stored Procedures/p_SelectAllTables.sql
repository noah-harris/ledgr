CREATE PROCEDURE [p_SelectAllTables]
AS
BEGIN

	DECLARE @table_name NVARCHAR(128)
	DECLARE @sql NVARCHAR(MAX)
	DECLARE [db_cursor] CURSOR FOR
	SELECT [name] FROM [sys].[tables] WHERE [type] = 'U' AND [name] <> 'days' ORDER BY [name]

	OPEN [db_cursor] FETCH NEXT FROM [db_cursor] INTO @table_name
	WHILE @@FETCH_STATUS = 0
	BEGIN
		SET @sql = 'SELECT * FROM ' + QUOTENAME(@table_name)
		EXEC sp_executesql @sql
		FETCH NEXT FROM [db_cursor] INTO @table_name
	END
	CLOSE [db_cursor]
	DEALLOCATE [db_cursor]

END