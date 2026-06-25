exec p_PercentComplete





SELECT
	StatementItemId,
	InvoiceId,
	PayeeId,
	MethodId,
	AccountDisplayName,
	StatementDate,
	MethodDisplayName,
	PayeeName,
	PayeeType,
	OrganizationTypeName,
	Segment,
	Category,
	TransactionDate,
	PostDate,
	ReferenceNumber,
	Description,
	Amount,
	ImageId,
	ImageFileName,
	ContentType,
	StatusType
FROM v_StatementItem 
WHERE 1=1 
	AND ImageId IS NULL 
	AND ISNULL(OrganizationTypeName, 'NULL') NOT IN (
	'EMPLOYER',
	''
	)
	AND PayeeName NOT IN (
	'COSTCO',
	'SHELL','EXXON',
	'TARGET',
	'')
	AND PayeeType <>'Account'
ORDER BY PayeeName, AccountDisplayName, MethodDisplayName, TransactionDate, Amount



SELECT 
	PayeeName, 
	''''+PayeeName+''',',
	COUNT(DISTINCT StatementItemId) AS [TotalItems], 
	SUM(CASE WHEN ImageId IS NULL THEN 1 ELSE 0 END) AS [TotalNullImageItems],
	SUM(CASE WHEN ImageId = dbo.NULL_IMAGE() THEN 1 ELSE 0 END) AS [TotalAssumedLostImages],
	SUM(CASE WHEN ISNULL(ImageId, dbo.NULL_IMAGE())  <> dbo.NULL_IMAGE() THEN 1 ELSE 0 END) AS [TotalMatchedImages]
FROM v_StatementItem 
WHERE 1=1
	AND PayeeType <>'Account'
GROUP BY PayeeName 
HAVING SUM(CASE WHEN ImageId IS NULL THEN 1 ELSE 0 END) > 0
--ORDER BY Count(DISTINCT StatementItemId) DESC
ORDER BY PayeeName


UPDATE StatementItem 
SET ImageId = dbo.NULL_IMAGE() 
WHERE StatementItemId IN (
	SELECT StatementItemId 
	FROM v_StatementItem 
	WHERE 1=1 
		and ImageId IS NULL
		AND PayeeName IN (

		)
)

