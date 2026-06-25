SELECT
	StatementItemId,
	AccountDisplayName,
	MethodDisplayName,
	PayeeName,
	TransactionDate,
	PostDate,
	ReferenceNumber,
	Description,
	Amount,
	ImageId
FROM v_StatementItem 
WHERE PayeeType = 'Account' ORDER BY ABS(AMount), Amount, TransactionDate