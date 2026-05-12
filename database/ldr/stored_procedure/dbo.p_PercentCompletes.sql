create procedure p_percent_complete 
as 


declare @pct_image varchar(50) =(cast(cast(
    ( -- Total completed statement items
        select count(*) 
        from statement_item as si
        where 1=1 
            and si.image_id is not null 
    )
        /
    ( -- Total statement items
        select count(*)*1.0 from statement_item
    )*100
as decimal(20,2)) as varchar(50))+'%')

declare @pct_invoice_image varchar(50) =(cast(cast(
    ( -- Total completed statement items
        select count(*) 
        from statement_item as si
        where 1=1 
            and si.image_id is not null 
            and si.invoice_id is not null 
    )
        /
    ( -- Total statement items
        select count(*)*1.0 from statement_item
    )*100
as decimal(20,2)) as varchar(50))+'%')


declare @pct varchar(50) =(cast(cast(
    ( -- Total completed statement items
        select count(*) 
        from statement_item as si
        where 1=1 
            and si.invoice_id is not null 
            and si.image_id is not null 
            and (select sum(ii.amount) from invoice_item as ii where ii.invoice_id = si.invoice_id group by ii.invoice_id) = si.amount
            and (select sum(ii.amount) from invoice_item as ii where ii.invoice_id = si.invoice_id group by ii.invoice_id) = (select i.total_amount_due from invoice as i where i.invoice_id = si.invoice_id)
    )
        /
    ( -- Total statement items
        select count(*)*1.0 from statement_item
    )*100
as decimal(20,2)) as varchar(50))+'%')


print('PERCENT IMAGE COMPLETE: '+@pct_image)
print('PERCENT INVOICE & IMAGE COMPLETE: '+@pct_invoice_image)
print('PERCENT COMPLETE: '+@pct)