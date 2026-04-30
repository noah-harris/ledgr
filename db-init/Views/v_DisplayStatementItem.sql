CREATE VIEW [v_DisplayStatementItem] AS
SELECT
    si.[StatementItemId],
	p.[PayeeName],
	p.[PayeeType],
	p.[Description] AS [PayeeDescription],
	si.[TransactionDate],
	si.[PostDate],
	si.[ReferenceNumber],
	ISNULL(c.[Symbol], '') + CAST(si.[Amount] AS VARCHAR(50)) AS [Amount],
	si.[Description] AS [StatementItemDescription],
	vo.[OrganizationName] AS [AccountOrganizationName],
	vo.[OrganizationTypeName] AS [AccountOrganizationTypeName], 
	a.[AccountNumber],
	COALESCE(a.[Description], act.[Description]) AS [AccountDescription],
	a.[StartDate] AS [AccountStartDate],
	a.[EndDate] AS [AccountEndDate],
	act.[AccountTypeName],
	a.[Currency],
	c.[Symbol] AS [CurrencySymbol],
	ISNULL(m.[MethodNumber], '') AS [MethodNumber],
	mt.[MethodTypeName],
	COALESCE(CASE WHEN ISNULL(m.[MethodNumber], '') = '' THEN NULL ELSE m.[MethodNumber] END, a.[AccountNumber]) AS [PaymentDisplayNumber],
	mt.[Description] AS [MethodDescription],
	vsi.[ImageFileName],
	vsi.[ContentType] AS [ImageContentType], 
	si.[InvoiceId],
	vsi.[ImageId]
FROM [StatementItem] AS si
JOIN [Statement]  AS s ON si.[StatementId] = s.[StatementId]
JOIN [Account] AS a ON s.[AccountId] = a.[AccountId]
JOIN [AccountType] AS act ON act.[AccountTypeId] = a.[AccountTypeId]
JOIN [Method] AS m ON si.[MethodId] = m.[MethodId]
JOIN [MethodType] AS mt ON mt.[MethodTypeId] = m.[MethodTypeId]
JOIN [v_Payee] AS p ON si.[PayeeId] = p.[PayeeId]
LEFT JOIN [v_Organization] AS vo ON vo.[OrganizationId] = a.[OrganizationId]
LEFT JOIN [v_Image] AS vsi ON vsi.[ImageId] = si.[ImageId]
LEFT JOIN [Currency] AS c ON c.[Currency] = a.[Currency];
