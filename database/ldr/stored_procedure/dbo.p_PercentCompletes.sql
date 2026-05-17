CREATE PROCEDURE [p_PercentComplete] 
    AS
BEGIN

    DECLARE @pct_image VARCHAR(50) =(cast(cast(
        ( -- Total completed statement items
            SELECT COUNT(*) 
            FROM [StatementItem] AS si
            WHERE si.[ImageId] IS NOT NULL 
        )
            /
        ( -- Total statement items
            SELECT COUNT(*)*1.0 from [StatementItem]
        )*100
    AS DECIMAL(20,2)) AS VARCHAR(50))+'%')

    DECLARE @pct_invoice_image VARCHAR(50) =(cast(cast(
        ( -- Total completed statement items
            SELECT COUNT(*) 
            FROM [StatementItem] AS si
            WHERE 1=1 
                AND si.ImageId IS NOT NULL 
                AND si.InvoiceId IS NOT NULL 
        )
            /
        ( -- Total statement items
            SELECT COUNT(*)*1.0 FROM [StatementItem]
        )*100
    AS DECIMAL(20,2)) AS VARCHAR(50))+'%')


    DECLARE @pct VARCHAR(50) =(cast(cast(
        ( -- Total completed statement items
            SELECT COUNT(*) 
            FROM [StatementItem] AS si
            WHERE 1=1 
                AND si.InvoiceId IS NOT NULL 
                AND si.ImageId IS NOT NULL
                AND (SELECT SUM(ii.Amount) FROM [InvoiceItem] AS ii WHERE ii.[InvoiceId] = si.[InvoiceId] GROUP BY ii.[InvoiceId]) = si.[Amount]
                AND (SELECT SUM(ii.Amount) FROM [InvoiceItem] AS ii WHERE ii.[InvoiceId] = si.[InvoiceId] GROUP BY ii.[InvoiceId]) = (SELECT i.[Amount] FROM [Invoice] AS i WHERE i.[InvoiceId] = si.[InvoiceId])
        )
            /
        ( -- Total statement items
            SELECT COUNT(*)*1.0 FROM [StatementItem]
        )*100
    AS DECIMAL(20,2)) AS VARCHAR(50))+'%')

    PRINT('PERCENT IMAGE COMPLETE: '+@pct_image)
    PRINT('PERCENT INVOICE & IMAGE COMPLETE: '+@pct_invoice_image)
    PRINT('PERCENT COMPLETE: '+@pct)

END