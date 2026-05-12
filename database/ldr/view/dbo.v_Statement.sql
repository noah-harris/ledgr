CREATE VIEW [v_Statement]
    AS
SELECT 
    s.[StatementId],
    s.[AccountId],
    va.[AccountDisplayName],
    'DATE: '+CONVERT(VARCHAR, s.[StatementDate], 23)+' | PERIOD: '+CONVERT(VARCHAR, s.[StartDate], 23)+' to '+CONVERT(VARCHAR, s.[EndDate], 23) AS [StatementDisplayName],
    s.[StatementDate],
    s.[StartDate],
    s.[EndDate],
    DATEDIFF(DAY, s.[StartDate], s.[EndDate]) + 1 AS [StatementPeriod],
    s.[StartBalance],
    s.[EndBalance],
    s.[EndBalance] - s.[StartBalance] AS [BalanceChange],
    s.[ImageId],
    vi.[ImageFileName]
FROM [Statement] AS s
JOIN [v_Account] AS va ON va.[AccountId] = s.[AccountId]
JOIN [v_Image] AS vi ON vi.[ImageId] = s.[ImageId]
