CREATE VIEW [v_Image]
    AS
SELECT 
	i.[UsersId],
	i.[ImageId],
	i.[FileName],
	i.[FileType],
	s.[StatusType],
	st.[StatusName],
	s.[ContentType],
	i.[FileName]+'.'+i.[FileType] AS [ImageFileName]
FROM [Image] AS i 
JOIN [ImageSort] AS s ON i.[ImageId] = s.[ImageId]
LEFT JOIN [ImageSortStatusType] AS st ON st.[StatusType] = s.[StatusType]
LEFT JOIN [ImageContentType] AS ct ON ct.[ContentType] = s.[ContentType]