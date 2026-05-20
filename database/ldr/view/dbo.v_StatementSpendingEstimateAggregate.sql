CREATE VIEW [v_StatementSpendingEstimateAggregate]
    AS
SELECT 
	[CalendarYear],
	[MonthName],
	[Segment],
	SUM([Amount]) AS [Amount]
FROM [v_StatementSpendingEstimate] AS a
GROUP BY [CalendarYear], [MonthName], [Segment]
