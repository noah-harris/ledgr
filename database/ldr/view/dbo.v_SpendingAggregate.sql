CREATE VIEW [v_SpendingAggregate] 
    AS
WITH CTE_Invoice_Multiplier AS (
	SELECT
		vsi.[InvoiceId],
		vsi.[TransactionDate],
		vsi.[PostDate],
		vsi.[PayeeName],
		vsi.[PayeeType],
		vsi.[Segment],
		vsi.[Category],
		vsi.[Amount] AS [Amount],
		(vsi.[Amount] / vi.[Amount]) AS [InvoiceMultiplier]
	FROM [v_StatementItem] AS vsi
	LEFT JOIN [v_Invoice] AS vi ON vi.[InvoiceId] = vsi.[InvoiceId]
),
CTE_Items AS (
	SELECT 
		cmi.[InvoiceId],
		cmi.[TransactionDate],
		cmi.[PostDate],
		cmi.[PayeeName],
		cmi.[PayeeType],
		COALESCE(vii.Segment, cmi.Segment) AS Segment,
		COALESCE(vii.Category, cmi.Category) AS Category,
		COALESCE(vii.SubCategory, 'UNCATEGORIZED') AS SubCategory,
		COALESCE(CAST(vii.[Amount] * cmi.[InvoiceMultiplier] AS DECIMAL(20,2)), cmi.[Amount]) AS [Amount]
	FROM CTE_Invoice_Multiplier AS cmi
	LEFT JOIN v_InvoiceItem AS vii ON cmi.InvoiceId = vii.InvoiceId
),
CTE_Dateless AS (
	SELECT
		[TransactionDate],
		Segment,
		Category,
		SubCategory,
		SUM(Amount) AS [Amount]
	FROM CTE_Items
	GROUP BY [TransactionDate],	Segment, Category, SubCategory
)
SELECT 
	CalendarYear,
	MonthName,
	Segment,
	SUM(Amount) AS Amount
FROM CTE_Dateless AS c
JOIN [Days] AS d ON d.[CalendarDate] = CAST([TransactionDate] AS DATE)
GROUP BY CalendarYear, MonthName, Segment