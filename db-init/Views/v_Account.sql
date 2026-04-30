CREATE VIEW [v_Account] 
    AS
SELECT 
	vu.[UsersId],
	a.[AccountId],
	a.[AccountTypeId],
	a.[OrganizationId],
	o.[OrganizationTypeId],
	o.[OrganizationName],
	vu.[FirstName],
	vu.[LastName],
	vu.[Username],
	at.[AccountTypeName],
	a.[AccountNumber],
	a.[Currency],
	a.[Description],
	a.[StartDate],
	a.[EndDate],
	UPPER(
		CASE 
			WHEN o.[OrganizationName] = at.[AccountTypeName] THEN at.[AccountTypeName]
			ELSE o.[OrganizationName] + ' - ' + at.[AccountTypeName]
		END + ' - ' + a.[AccountNumber]
	) AS [AccountDisplayName]
FROM [Account] AS a
JOIN [AccountType] AS at ON a.[AccountTypeId] = at.[AccountTypeId]
JOIN [Organization] AS o ON o.[OrganizationId] = a.[OrganizationId]
JOIN [v_Users] AS vu ON vu.[UsersId] = a.[UsersId]


