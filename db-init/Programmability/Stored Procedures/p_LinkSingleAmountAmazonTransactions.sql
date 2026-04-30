CREATE PROCEDURE [p_link_single_amount_amazon_transactions]
	AS
update si
set 
	image_id = '0F0525F5-EFD9-DB87-71AA-8E28390FB3A1', 
	si.invoice_id = i.invoice_id
from statement_item as si
left join method as m on m.method_id = si.method_id
left join invoice as i 
on 1=1 
	and i.payee_id = si.payee_id
	and i.notes = m.amazon_alias
	and i.total_amount_due = si.amount
where 1=1 
	and i.notes <> ''
	and si.invoice_id is null
	and si.payee_id = '4900F18E-A67D-D3DF-C0BB-02F6E9C7B23D'
	and (select count(*) from invoice as i where i.total_amount_due = si.amount and i.notes = m.amazon_alias and i.payee_id = '4900F18E-A67D-D3DF-C0BB-02F6E9C7B23D') = (select count(*) from statement_item as si1 where si1.amount = si.amount and si1.method_id = m.method_id and si1.payee_id = '4900F18E-A67D-D3DF-C0BB-02F6E9C7B23D')
	and (select count(*) from statement_item as si1 where si1.amount = si.amount and si1.method_id = m.method_id and si1.payee_id = '4900F18E-A67D-D3DF-C0BB-02F6E9C7B23D') = 1
