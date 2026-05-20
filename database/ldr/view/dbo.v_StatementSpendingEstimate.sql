CREATE VIEW [v_StatementSpendingEstimate]
	AS
SELECT
	--[UsersId]
	d.[CalendarDate],
	d.[CalendarYear],
	d.[CalendarQuarter],
	d.[CalendarMonth],
	d.[MonthName],
	d.[DayOfMonth],
	d.[DayOfWeek],
	d.[DayName],
	vsi.[TransactionDate],
	vsi.[PostDate],
	vsi.[PayeeName],
	vsi.[PayeeType],
	vsi.[ORganizationTypeName],
	vsi.[Segment],
	vsi.[Category],
	vsi.[Amount]
FROM [v_StatementItem] AS vsi
JOIN [Days] AS d ON d.[CalendarDate] = CAST(vsi.[TransactionDate] AS DATE)