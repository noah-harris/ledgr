CREATE PROCEDURE [p_StatementPeriodBalanceCheck]
	AS
SET NOCOUNT ON;

BEGIN

	SELECT 
		vs.[AccountDisplayName] AS [Account], 
		vs.[StatementDate] AS [Statement Date], 
		SUM([Amount]) AS [Statement Item Amount Total], 
		MAX(vs.BalanceChange) AS [Statement Balance Change]
	FROM [dbo].[StatementItem] AS si
	JOIN [dbo].[v_Statement] AS vs 
	ON vs.[StatementId] = si.[StatementId]
	GROUP BY vs.[AccountDisplayName], vs.[StatementDate], vs.[EndBalance], vs.[StartBalance]
	HAVING SUM([Amount]) <> vs.[EndBalance] - vs.[StartBalance]
	ORDER BY [Account], [Statement Date]

END