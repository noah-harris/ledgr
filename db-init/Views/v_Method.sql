CREATE VIEW [v_Method] 
    AS
SELECT 
    m.[AccountId],
    va.[AccountTypeId],
    m.[MethodId], 
    m.[MethodTypeId], 
    va.[AccountDisplayName],
    va.[AccountTypeName],
    mt.[MethodTypeName],
    atmt.[DefaultMethodName],
    atmt.[DefaultMethodName] + CASE WHEN (ISNULL(m.[MethodNumber], '') != '') THEN ' - ' + m.[MethodNumber] ELSE '' END AS [MethodDisplayName],
    m.[MethodNumber], 
    atmt.[IsAccountTransferMethod],
    m.[AmazonPaymentMethod], 
    m.[ImageId]
FROM [Method] AS m
JOIN [v_Account] AS va ON m.[AccountId] = va.[AccountId]
JOIN [AccountTypeMethodTypeTemplate] AS atmt ON va.[AccountTypeId] = atmt.[AccountTypeId] AND m.[MethodTypeId] = atmt.[MethodTypeId]
JOIN [MethodType] AS mt ON m.[MethodTypeId] = mt.[MethodTypeId]
