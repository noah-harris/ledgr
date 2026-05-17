CREATE PROCEDURE [p_MissingStatementCheck] 
AS
SET NOCOUNT ON;

BEGIN 

	;WITH [ExpectedDays] AS (
		SELECT
			a.[AccountId],
			d.[CalendarDate]
		FROM [dbo].[v_Account] AS a
		JOIN [dbo].[Days] AS d
		ON 1=1 
			AND d.[CalendarDate] >= a.[StartDate]
			AND d.[CalendarDate] <= ISNULL(a.[EndDate], GETDATE())
		WHERE d.[CalendarDate] <= GETDATE()
	),
	[MissingDays] AS (
		SELECT *
		FROM [ExpectedDays] AS e
		WHERE NOT EXISTS (
			SELECT NULL
			FROM [dbo].[Statement] AS s
			WHERE 1=1 
				AND s.[AccountId] = e.[AccountId]
				AND e.[CalendarDate] BETWEEN s.[StartDate] AND s.[EndDate]
		)
	),
	[numbered] AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY [AccountId] ORDER BY [CalendarDate]) AS rn FROM [MissingDays]),
	[grouped] AS (SELECT *, DATEADD(DAY, -rn, [CalendarDate]) AS grp FROM [numbered])
	SELECT
		[AccountDisplayName],
		(SELECT MAX([StatementDate]) FROM [dbo].[v_Statement] AS vs WHERE g.[AccountId] = vs.[AccountId]) AS [LastStatementDate],
		MIN([CalendarDate]) AS [gap_start],
		MAX([CalendarDate]) AS [gap_end],
		COUNT(*) AS [gap_length]
	FROM [grouped] AS g
	JOIN [dbo].[v_Account] AS a ON a.[AccountId] = g.[AccountId]
	GROUP BY [AccountDisplayName], g.[AccountId], [grp]
	HAVING COUNT(*) > 31
	ORDER BY [AccountDisplayName], [gap_start];

	-- ;WITH [CTE_statement_item] AS (
	-- 	SELECT 
	-- 		[AccountId], 
	-- 		[StatementDate], 
	-- 		(SELECT COUNT(*) FROM [dbo].[StatementItem] AS si WHERE 1=1 AND si.[AccountId] = s.[AccountId] AND si.[StatementDate] = s.[StatementDate]) AS [transactions]
	-- 	FROM [dbo].[Statement] AS s
	-- 	GROUP BY [AccountId], [StatementDate]
	-- )
	-- SELECT 
	-- 	*, 
	-- 	si.[transactions] 
	-- FROM [dbo].[v_Statement] AS s 
	-- LEFT JOIN [CTE_statement_item] AS si 
	-- ON 1=1 
	-- 	AND si.[AccountId] = s.[AccountId] 
	-- 	AND si.[StatementDate] = s.[StatementDate]
	-- ORDER BY s.[AccountId], s.[StatementDate] 

END