create procedure p_generate_subscription_invoices (
	@payee_name varchar(50),
	@amount decimal(20,2),
	@category_display_name varchar(50),
	@invoice_description varchar(255) = '',
	@invoice_item_description varchar(255) = ''
)

AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

			declare @category_id uniqueidentifier 
			select @category_id = category_id
			from v_invoice_item_category
			where category_display_name = @category_display_name

			if @category_id is null
			begin
				select 1/0
			end

			-- Get invoices
			drop table if exists #invoices
			select 
				payee_name,
				transaction_date as invoice_date,
				cast(null as date) as due_date,
				reference_number as invoice_number,
				amount as total_amount_due,
				@invoice_description as description,
				cast(null as datetime2(0)) as start_date,
				cast(null as datetime2(0)) as end_date,
				'noimage.jpg' as unhashed_image_id,
				'AUTO GENERATED INVOICE' as notes
			into #invoices
			from v_statement_item as vsi
			where 1=1 
				and amount = @amount
				and payee_name = @payee_name
				and invoice_id is null
				and not exists (
					select null
					from invoice as i
					where 1=1
						and i.payee_id = vsi.payee_id
						and i.invoice_date = vsi.transaction_date
						and i.total_amount_due = vsi.amount
					)

			-- generate invoices
			insert into v_invoice (payee_name, invoice_date, due_date, invoice_number, total_amount_due, description, start_date, end_date, unhashed_image_id, notes)
			select * from #invoices

			-- get generated invoices
			drop table if exists #new_invoices
			select * 
			into #new_invoices
			from v_invoice as vi 
			where exists (
				select null 
				from #invoices as i
				where 1=1 
					and i.payee_name = vi.payee_name
					and i.invoice_date = vi.invoice_date 
					and i.total_amount_due = vi.total_amount_due
			)

			insert into v_invoice_item(invoice_id, item_id, category_id, description, quantity, amount, display_order, notes)
			select 
				invoice_id,
				newid() as item_id,
				@category_id as category_id,
				@invoice_item_description as description,
				1 as quantity,
				total_amount_due as amount,
				1 as display_order,
				'GENERATED invoice_item' as notes
			from #new_invoices

			-- update statement_items with generated invoices
			update si set 
				si.invoice_id = ni.invoice_id, 
				si.image_id = ni.image_id
			from statement_item as si
			join #new_invoices as ni
			on 1=1
				and ni.payee_id = si.payee_id
				and ni.invoice_date = si.transaction_date
				and ni.total_amount_due = si.amount

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        THROW;
    END CATCH;
END;


