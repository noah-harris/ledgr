CREATE PROCEDURE [p_AccountTransfertValidation] 
AS
SET NOCOUNT ON;

WITH [CTE_Transfer] as (
	SELECT 
		vsi.[AccountId] AS [FROM ACCOUNT],
		vsi.[StatementDate] AS [STATEMENT DATE],
		vsi.[StatementId] AS [STATEMENT ID],
		vsi.[TransactionDate] AS [TRANSACTION DATE],
		vsi.[PostDate] AS [POST DATE],
		vsi.[MethodId] AS [METHOD],
		vp.[PayeeId] AS [TO ACCOUNT],
		vsi.[Amount] AS [AMOUNT],
		vs.[ImageId]
	FROM [v_StatementItem] as vsi 
	LEFT JOIN [v_Statement] AS vs ON vs.[StatementId] = vsi.[StatementId]
	JOIN [v_Payee] as vp on vp.[PayeeId] = vsi.[PayeeId]
	WHERE 1=1 
		AND (vp.[PayeeType] = 'account' /*OR vp.[PayeeName] = 'UNKNOWN'*/)
		AND vp.[PayeeName] NOT IN ('VENMO', 'USACASH')
)
SELECT 
	f.*,
	'H:\My Drive\BudgetTool\IMAGE\ARCHIVE\STATEMENT\'+vi.[ImageFileName] AS [statement_img]
FROM [CTE_Transfer] AS f
LEFT JOIN [v_image] AS vi ON vi.[ImageId] = f.[ImageId]
WHERE 1=1
	AND NOT EXISTS (
		SELECT NULL
		FROM [CTE_Transfer] as t
		WHERE 1=1
			AND f.[TO ACCOUNT] = t.[FROM ACCOUNT]
			AND ABS(f.[AMOUNT]) = ABS(t.[AMOUNT])
			AND f.[TRANSACTION DATE] = t.[TRANSACTION DATE]
		)
	AND EXISTS (
		SELECT NULL
		FROM [v_Statement] AS vs
		WHERE 1=1
			AND vs.[AccountId] = f.[TO ACCOUNT]
			AND f.[TRANSACTION DATE] BETWEEN vs.[StartDate]  AND vs.[EndDate]
		)
ORDER BY [STATEMENT DATE], ABS(f.[AMOUNT]) DESC, f.[FROM ACCOUNT], f.[TRANSACTION DATE]