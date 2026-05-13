CREATE VIEW [v_Payee] 
    AS
SELECT 
    [PayeeId],
    CASE
        WHEN p.[PayeeType] = 'Organization' THEN o.[OrganizationName]
        WHEN p.[PayeeType] = 'Account' THEN a.[AccountDisplayName]
        WHEN p.[PayeeType] = 'Users' THEN u.[FirstName] + ' ' + u.[LastName]
        ELSE NULL
    END AS [PayeeName],
    [PayeeType],
    CASE
        WHEN p.[PayeeType] = 'Organization' THEN o.[OrganizationTypeName]
        ELSE NULL
    END AS [OrganizationTypeName],
    
    CASE
        WHEN p.[PayeeType] = 'Organization' THEN o.[IsAccountProvider]
        ELSE 0
    END AS [IsAccountProvider],

    CASE
        WHEN p.[PayeeType] = 'Organization' THEN o.[Segment]
        WHEN p.[PayeeType] = 'Account' THEN 'BANKING'
        WHEN p.[PayeeType] = 'Users' THEN 'PERSONAL'
        ELSE NULL
    END AS [Segment],

    CASE
        WHEN p.[PayeeType] = 'Organization' THEN o.[Description]
        WHEN p.[PayeeType] = 'Account' THEN a.[Description]
        WHEN p.[PayeeType] = 'Users' THEN 'Users: ' + u.[Email]
        ELSE NULL
    END AS [Description]
FROM [Payee] AS p
LEFT JOIN [v_Organization] AS o ON p.[PayeeId] = o.[OrganizationId] AND p.[PayeeType] = 'Organization'
LEFT JOIN [v_Account] AS a ON p.[PayeeId] = a.[AccountId] AND p.[PayeeType] = 'Account'
LEFT JOIN [Users] AS u ON p.[PayeeId] = u.[UsersId] AND p.[PayeeType] = 'Users'