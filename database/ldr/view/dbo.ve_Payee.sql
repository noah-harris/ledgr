CREATE VIEW [ve_Payee] AS

    SELECT 
        CAST(NULL AS UNIQUEIDENTIFIER) AS [PayeeId],
        CAST(NULL AS NVARCHAR(50)) AS [PayeeName],
        CAST(NULL AS VARCHAR(50)) AS [PayeeType],
        CAST(NULL AS NVARCHAR(255)) AS [Description]