
/*
==================================================
IMAGE ID CONVERSION - I messed up and stripped non alphanumeric characters from the unhashed uuids.

In windows its unique based on LOWER(FileName.FileType) so we can just hash the original filename and filetype to get the correct image ids.
==================================================
*/
IF (SELECT COUNT(*) FROM [ldr].[dbo].[Currency]) > 0
BEGIN
	PRINT 'Tables already have data. Skipping seeding.'
	RETURN
END

DROP TABLE IF EXISTS [import].[image]
SELECT 
	[image_id], 
	CAST(
		HASHBYTES('MD5', 
		CAST(LOWER([original_filename]+'.'+[filetype]) AS NVARCHAR(861))
		)
	AS UNIQUEIDENTIFIER)
	AS [NewImageId]
INTO [import].[image]
FROM [BudgetTool].[btl].[dbo].[image]

UPDATE imgs
SET 
	imgs.[StatusType] = CASE WHEN vi.[sort_status] = 'm' THEN 'c' ELSE vi.[sort_status] END, 
	imgs.[ContentType] = UPPER(vi.[entity_type])
FROM [ldr].[dbo].[ImageSort] AS imgs 
JOIN [import].[image] AS img ON img.[NewImageId] = imgs.[ImageId]
JOIN [BudgetTool].[btl].[dbo].[v_image] AS vi ON img.[image_id] = vi.[image_id]

UPDATE ni SET ni.[ImageId] = img.[NewImageId] 
FROM [ldr].[dbo].[Invoice] AS ni
LEFT JOIN [BudgetTool].[btl].[dbo].[invoice] AS i ON i.[invoice_id] = ni.[InvoiceId]
LEFT JOIN [import].[image] AS img ON img.[image_id] = i.[image_id]

UPDATE ns SET ns.[ImageId] = img.[NewImageId] 
FROM [ldr].[dbo].[Statement] AS ns
LEFT JOIN [BudgetTool].[btl].[dbo].[statement] AS s ON s.[statement_id] = ns.[StatementId]
LEFT JOIN [import].[image] AS img ON img.[image_id] = s.[image_id]

UPDATE nm SET nm.[ImageId] = img.[NewImageId] 
FROM [ldr].[dbo].[Method] AS nm
LEFT JOIN [BudgetTool].[btl].[dbo].[method] AS m ON m.[method_id] = nm.[MethodId]
LEFT JOIN [import].[image] AS img ON img.[image_id] = m.[image_id]

UPDATE nsi SET nsi.[ImageId] = img.[NewImageId] 
FROM [ldr].[dbo].[StatementItem] AS nsi
LEFT JOIN [BudgetTool].[btl].[dbo].[statement_item] AS si ON si.[transaction_id] = nsi.[StatementItemId]
LEFT JOIN [import].[image] AS img ON img.[image_id] = si.[image_id]

UPDATE [ldr].[dbo].[Method] SET [ImageId] = '7B39EEC4-8748-805D-7A58-F6681F5354F4' WHERE [MethodId] = 'F3467A2B-1434-8FDA-EDEC-E549604BC0F1'

UPDATE [ldr].[dbo].[Method] SET [ImageId] = '2740391C-72F7-3986-62E4-1DA7F8D1C57C' WHERE [ImageId] IS NULL