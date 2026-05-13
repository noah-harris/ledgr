CREATE PROCEDURE [p_statement_period_balance_check]
	AS
SET NOCOUNT ON;

BEGIN

	SELECT 
		s.[account_display_name] AS [Account], 
		si.[statement_date] AS [Statement Date], 
		SUM([amount]) AS [Statement Item Amount Total], 
		MAX(s.period_balance_change) AS [Statement Balance Change]
	FROM [dbo].[statement_item] AS si
	JOIN [dbo].[v_statement] AS s 
	ON 1=1 
		AND si.[account_id] = s.[account_id] 
		AND si.[statement_date] = s.[statement_date]
	GROUP BY s.[account_display_name], si.[statement_date], s.[period_end_balance], s.[period_start_balance]
	HAVING SUM([amount]) <> s.[period_end_balance] - s.[period_start_balance]
	ORDER BY [Account], [Statement Date]

END