

-- This is to be run on the other db
-- MAKE ALL IDENTIFIERS IN BRACKETS
-- MAKE ALL SQL KEYWORDS UPPERCASE
/*
==================================================
CURRENCY
==================================================
*/
-- Use arbitrary table to skip seeding for tall tables if there is data in it.
IF (SELECT COUNT(*) FROM [ldr].[dbo].[Currency]) > 0
BEGIN
	PRINT 'Tables already have data. Skipping seeding.'
	RETURN
END



INSERT INTO [ldr].[dbo].[Currency] ([Currency], [Symbol]) VALUES
('USD', '$'),
('EUR', '€'),
('GBP', '£'),
('JPY', '¥'),
('CAD', 'CA$'),
('AUD', 'A$'),
('CHF', 'CHF'),
('CNY', '¥'),
('INR', '₹'),
('MXN', 'MX$'),
('BRL', 'R$'),
('KRW', '₩'),
('SEK', 'kr'),
('NOK', 'kr'),
('DKK', 'kr'),
('NZD', 'NZ$'),
('SGD', 'S$'),
('HKD', 'HK$'),
('ZAR', 'R'),
('RUB', '₽')

/*
==================================================
USERS
==================================================
*/

INSERT INTO [ldr].[dbo].[Users] VALUES 
('40B6C17C-98E7-482C-BA22-E66603D4173C', 'XMENTROPY', 'noahharris9811@gmail.com', 'NOAH', 'HARRIS'),
('E39F5E23-A6D6-4F52-8E4B-72910BF30AFB', 'CCMILLER', 'ccmiller123@gmail.com', 'CLAIRE', 'MILLER')

DROP TABLE IF EXISTS #new_users
SELECT *
INTO #new_users
FROM [BudgetTool].[btl].[dbo].[payee]
WHERE 1=2 
	OR (1=1
		AND [payee_type] = 'person' 
		AND [payee_name] NOT IN ('CLAIRE MILLER', 'NOAH HARRIS')
	)
	OR (
		[payee_name] IN (
			'DAWN DIXON',
			'HANNAH TILANDER',
			'NICHOLAS WHITMER'
		)
	)

INSERT INTO [ldr].[dbo].[Users]
SELECT 
	[payee_id] AS [UserId], 
	LEFT([payee_name], CHARINDEX(' ', [payee_name])-1) + '_' + RIGHT([payee_name], LEN([payee_name])-CHARINDEX(' ', [payee_name])) + '_01' AS [Username],
	'' AS [Email],
	LEFT([payee_name], CHARINDEX(' ', [payee_name])-1) as [FirstName],
	RIGHT([payee_name], LEN([payee_name])-CHARINDEX(' ', [payee_name])) AS [LastName]
FROM #new_users

/*
==================================================
OrganizationType
==================================================
*/

INSERT INTO [ldr].[dbo].[OrganizationType] VALUES
('3342BFBF-C3C9-4B04-9B7C-E7CBCE629922','BANK',1,'BANKING','Physical bank. SECU Wells Fargo etc.'),
('AB4656C8-B7B8-47B2-9179-21EDA340E075','VIRTUAL WALLET',1,'BANKING','Venmo paypal etc.'),
('6B5949DE-A2D0-4EFB-BDA7-870CA32399B8','FEDERAL RESERVE',1,'BANKING','Physical cash is owned by the federal reserve. This is used to categorize cash accounts.'),
('591F2E2F-4D22-42E6-A6C1-82731A4EDD4D','RESTAURANT',0,'DINING','A simple restaurant or food service establishment'),
('AA3F6DFF-AE03-45C9-8CE8-9CD33E0CA124','ONLINE RETAIL',0,'UNCATEGORIZED','A simple online retail establishment'),
('1BFE750E-EEFF-4D27-8139-C0A13CB5AC79','PLACEHOLDER',0,'UNCATEGORIZED','PLACEHOLDER')

DECLARE @BANK UNIQUEIDENTIFIER = (SELECT [OrganizationTypeId] FROM [ldr].[dbo].[OrganizationType] WHERE [OrganizationTypeName] = 'BANK')
DECLARE @VIRTUAL_WALLET UNIQUEIDENTIFIER = (SELECT [OrganizationTypeId] FROM [ldr].[dbo].[OrganizationType] WHERE [OrganizationTypeName] = 'VIRTUAL WALLET')
DECLARE @FEDERAL_RESERVE UNIQUEIDENTIFIER = (SELECT [OrganizationTypeId] FROM [ldr].[dbo].[OrganizationType] WHERE [OrganizationTypeName] = 'FEDERAL RESERVE')
DECLARE @RESTAURANT UNIQUEIDENTIFIER = (SELECT [OrganizationTypeId] FROM [ldr].[dbo].[OrganizationType] WHERE [OrganizationTypeName] = 'RESTAURANT')
DECLARE @PLACEHOLDER UNIQUEIDENTIFIER = (SELECT [OrganizationTypeId] FROM [ldr].[dbo].[OrganizationType] WHERE [OrganizationTypeName] = 'PLACEHOLDER')
DECLARE @ONLINE_RETAIL UNIQUEIDENTIFIER = (SELECT [OrganizationTypeId] FROM [ldr].[dbo].[OrganizationType] WHERE [OrganizationTypeName] = 'ONLINE RETAIL')
/*
==================================================
Organization
==================================================
*/

INSERT INTO [ldr].[dbo].[Organization] VALUES
('5B1283A7-CA58-4873-A95F-DB7063CB4A4D', 'USA', @FEDERAL_RESERVE, ''),
('52E8B036-41D1-46CD-B6E4-642D1740C821', 'CITI', @BANK, ''),
('91062035-FFEE-4DA3-B5C0-FB25341111B8', 'PAYPAL', @VIRTUAL_WALLET, ''),
('BB4B4DA0-C4B8-D804-8BCC-175905514EF0', 'VENMO', @VIRTUAL_WALLET, '')


INSERT INTO [ldr].[dbo].[Organization]
SELECT 
	[payee_id] AS [OrganizationId], 
	[payee_name] AS [OrganizationName], 
	'1BFE750E-EEFF-4D27-8139-C0A13CB5AC79' AS [OrganizationTypeId], 
	'' AS [Description]
FROM [BudgetTool].[btl].[dbo].[payee]
WHERE 1=1 
	AND [payee_type] = 'organization'
	AND [payee_name] NOT IN (
			'DAWN DIXON',
			'HANNAH TILANDER',
			'NICHOLAS WHITMER'
		)

UPDATE [ldr].[dbo].[Organization]
SET 
	[OrganizationTypeId] = 
	CASE
		WHEN [OrganizationName] = 'WELLS FARGO' THEN @BANK
		WHEN [OrganizationName] = 'SECU' THEN @BANK
		WHEN [OrganizationName] = 'AMAZON' THEN @ONLINE_RETAIL
		ELSE [OrganizationTypeId]
	END

/*
==================================================
Account Type
==================================================
*/

INSERT INTO [ldr].[dbo].[AccountType] ([AccountTypeId], [AccountTypeName], [IsCredit], [Description]) VALUES
('A1044F6A-8370-4526-8D62-117A925FBEDD', 'CHECKING',            0, 'Standard checking account'),
('58EAF299-B68D-43F3-A513-4E783B585CFE', 'SAVINGS',             0, 'Savings account'),
('6ED11311-FBAB-4411-B339-CA810A655AE0', 'CREDIT CARD',         1, 'Revolving credit account'),
('745DA158-6D85-412E-A895-4045D01B74F6', 'VENMO',               0, 'Venmo digital wallet'),
('3AFC0E73-28EC-4D4E-9662-85F3937D5086', 'PAYPAL',              0, 'PayPal digital wallet'),
('4C0EB8FA-41E1-45C2-BB20-5914519B5402', 'WALLET',              0, 'Physical cash wallet'),
('D4C6EE81-A165-43C4-9F11-5BC7FCB804E0', 'CREDIT CARD REWARDS', 0, 'Credit card rewards account'),
('62FA9A3E-7864-4EEE-A30C-87B783EA4A80', 'CD',                  0, 'Certificate of Deposit account');


/*
==================================================
ACCOUNT
==================================================
*/
INSERT INTO [ldr].[dbo].[Account]
SELECT 
	CASE
		WHEN [unhashed_account_id] = 'CITICREDIT' THEN 'E39F5E23-A6D6-4F52-8E4B-72910BF30AFB'
		WHEN [unhashed_account_id] = 'PAYPALNOAH' THEN '40B6C17C-98E7-482C-BA22-E66603D4173C'
		WHEN [unhashed_account_id] = 'SECUCHECKING44153121' THEN 'E39F5E23-A6D6-4F52-8E4B-72910BF30AFB'
		WHEN [unhashed_account_id] = 'SECUCREDIT4046571150920401' THEN 'E39F5E23-A6D6-4F52-8E4B-72910BF30AFB'
		WHEN [unhashed_account_id] = 'SECUSHARE60559787' THEN 'E39F5E23-A6D6-4F52-8E4B-72910BF30AFB'
		WHEN [unhashed_account_id] = 'USACASH' THEN '40B6C17C-98E7-482C-BA22-E66603D4173C'
		WHEN [unhashed_account_id] = 'VENMOCLAIREccmiller123' THEN 'E39F5E23-A6D6-4F52-8E4B-72910BF30AFB'
		WHEN [unhashed_account_id] = 'VENMONOAH' THEN '40B6C17C-98E7-482C-BA22-E66603D4173C'
		WHEN [unhashed_account_id] = 'WELLSFARGOCHECKING8809559209' THEN '40B6C17C-98E7-482C-BA22-E66603D4173C'
		WHEN [unhashed_account_id] = 'WELLSFARGOCREDIT4147181618346534' THEN '40B6C17C-98E7-482C-BA22-E66603D4173C'
		WHEN [unhashed_account_id] = 'WELLSFARGOREWARDS60022716268' THEN '40B6C17C-98E7-482C-BA22-E66603D4173C'
		WHEN [unhashed_account_id] = 'WELLSFARGOSAVINGS1810566578' THEN '40B6C17C-98E7-482C-BA22-E66603D4173C'
		WHEN [unhashed_account_id] = 'WELLSFARGOTIMEACCOUNT5558' THEN '40B6C17C-98E7-482C-BA22-E66603D4173C'
		ELSE NULL 
	END AS [UsersId],
	[account_id] as [AccountId],
	CASE
		WHEN [unhashed_account_id] = 'CITICREDIT' THEN '6ED11311-FBAB-4411-B339-CA810A655AE0'
		WHEN [unhashed_account_id] = 'PAYPALNOAH' THEN '3AFC0E73-28EC-4D4E-9662-85F3937D5086'
		WHEN [unhashed_account_id] = 'SECUCHECKING44153121' THEN 'A1044F6A-8370-4526-8D62-117A925FBEDD'
		WHEN [unhashed_account_id] = 'SECUCREDIT4046571150920401' THEN '6ED11311-FBAB-4411-B339-CA810A655AE0'
		WHEN [unhashed_account_id] = 'SECUSHARE60559787' THEN '58EAF299-B68D-43F3-A513-4E783B585CFE'
		WHEN [unhashed_account_id] = 'USACASH' THEN '4C0EB8FA-41E1-45C2-BB20-5914519B5402'
		WHEN [unhashed_account_id] = 'VENMOCLAIREccmiller123' THEN '745DA158-6D85-412E-A895-4045D01B74F6'
		WHEN [unhashed_account_id] = 'VENMONOAH' THEN '745DA158-6D85-412E-A895-4045D01B74F6'
		WHEN [unhashed_account_id] = 'WELLSFARGOCHECKING8809559209' THEN 'A1044F6A-8370-4526-8D62-117A925FBEDD'
		WHEN [unhashed_account_id] = 'WELLSFARGOCREDIT4147181618346534' THEN '6ED11311-FBAB-4411-B339-CA810A655AE0'
		WHEN [unhashed_account_id] = 'WELLSFARGOREWARDS60022716268' THEN 'D4C6EE81-A165-43C4-9F11-5BC7FCB804E0'
		WHEN [unhashed_account_id] = 'WELLSFARGOSAVINGS1810566578' THEN '58EAF299-B68D-43F3-A513-4E783B585CFE'
		WHEN [unhashed_account_id] = 'WELLSFARGOTIMEACCOUNT5558' THEN '62FA9A3E-7864-4EEE-A30C-87B783EA4A80'
		ELSE NULL 
	END AS [AccountTypeId],
	(SELECT TOP 1 [OrganizationId] from [ldr].[dbo].[Organization] where [OrganizationName] = [bank_name]) AS [OrganizationId],
	[account_number] as [AccountNumber],
	[currency] as [Currency],
	[notes] as [Description],
	[effective_start_date] AS [StartDate],
	[effective_end_date] as [EndDate]
FROM [BudgetTool].[btl].[dbo].[v_account]

INSERT INTO [ldr].[dbo].[Account] VALUES ('E39F5E23-A6D6-4F52-8E4B-72910BF30AFB', '2B6A9E7A-9229-45E6-9F37-6390105C5204', '4C0EB8FA-41E1-45C2-BB20-5914519B5402', '5B1283A7-CA58-4873-A95F-DB7063CB4A4D', 'CLAIREWALLET1', 'USD', 'This is Claire''s wallet. It has lots of cash.', '2025-01-01 00:00:00', '2050-12-31 23:59:59') -- Claire Cash

UPDATE [ldr].[dbo].[Account] SET [AccountNumber] = 'noahharris9811@gmail.com' WHERE [AccountId] = '8A1B3DA0-68D8-D0BB-890D-B71101EDE17D' --NOAH PAYPAL
UPDATE [ldr].[dbo].[Account] SET [AccountNumber] = '4100 3902 6443 9361' WHERE [AccountId] = '616B7B4A-2E64-3C4D-EB19-5E4EEC71BCC6' --Claire Citi credit
UPDATE [ldr].[dbo].[Account] SET [AccountNumber] = 'NOAHWALLET1' WHERE [AccountId] = '30AA8CA1-C196-4D39-3F83-CE2FD4217824' --NOAH WALLET
UPDATE [ldr].[dbo].[Account] SET [AccountNumber] = '@Noah_Harris01' WHERE [AccountId] = 'E2CE3A14-65AC-FF67-14D4-4DDF04272E2A' --NOAH Venmo

UPDATE [ldr].[dbo].[Account] SET [Description] = 'This is Claire''s SECU savings account.' WHERE [AccountId] = 'CE991F09-8D78-35CB-A3D6-0FE1E975ED0C' --CLAIRE SECU SAVINGS
UPDATE [ldr].[dbo].[Account] SET [Description] = 'This is Claire''s Venmo account.' WHERE [AccountId] = '09EF63AD-483C-168F-C36C-62415C21004E' --CLAIRE VENMO
UPDATE [ldr].[dbo].[Account] SET [Description] = 'This is Noah''s Paypal account.' WHERE [AccountId] = '8A1B3DA0-68D8-D0BB-890D-B71101EDE17D' --NOAH WELLS Paypal
UPDATE [ldr].[dbo].[Account] SET [Description] = 'This is Noah''s CD account. It is closed.' WHERE [AccountId] = '8F8F87DB-0CF6-A8E9-956F-FD2F81B6685C' --NOAH CD

/*
==================================================
DAYS
==================================================
*/
INSERT INTO [ldr].[dbo].[Days]
SELECT * FROM [BudgetTool].[btl].[dbo].[days]


/*
==================================================
METHOD TYPE
==================================================
*/

-- Should be uppercase
INSERT INTO [ldr].[dbo].[MethodType] ([MethodTypeId], [MethodTypeName], [Description]) VALUES
('1E3B4612-5F2F-400B-84EC-DE06C4DD8269', 'TRANSACTION', 'A basic transaction.'),
('76712111-DC2B-4EB4-9578-DDB2FAAA987A', 'CHECK', 'Paper check'),
('0DAFA787-2D16-450E-A91D-C32B074151A8', 'ACH TRANSFER', 'Electronic bank transfer'),
('E6144C21-7150-4284-8ED0-952990CEF9E0', 'WIRE TRANSFER', 'Wire transfer'),
('5BB7F1A4-CF18-44A9-A960-F2FE99978A99', 'CASH WITHDRAWAL', 'Cash withdrawn from account'),
('4F89DF75-BC8C-4716-9369-D11D6A2D4C4A', 'CASH DEPOSIT', 'Cash deposited into account'),
('E23C9359-DFCA-41C4-BBC9-0C08E35FB57E', 'TRANSFER', 'Peer-to-peer or internal transfer'),
('0414778E-4FE3-4AFB-873F-541CEE9B16B2', 'BALANCE TRANSFER', 'Transfer out to linked bank'),
('FC4F0816-BB40-4A04-8EB7-E196E1A3FA3C', 'CASH', 'Physical cash transaction'),
('7AE4A186-62A0-46FB-9377-504A25BB2846', 'BALANCE PAYMENT', 'Direct payment or charge on credit'),
('1CA1C35D-C8D4-481E-AE61-3DF6D5510A22', 'CASH BACK EARNINGS', 'Cash back reward from credit card'),
('1EF0E2F5-4B9C-4064-B8EC-6A68CBDCEA4C', 'CASH BACK REDEMPTION', 'Redemption of rewards points'),
('47B12EE7-66F6-4AE3-8334-F5B23553E5CF', 'INTEREST', 'Interest payment or charge')


/*
==================================================
ACCOUNT TYPE METHOD TYPE TEMPLATE
==================================================
*/
-- Should be uppercase
DECLARE @Checking UNIQUEIDENTIFIER = (SELECT [AccountTypeId] FROM [ldr].[dbo].[AccountType] WHERE [AccountTypeName] = 'CHECKING');
DECLARE @Savings UNIQUEIDENTIFIER = (SELECT [AccountTypeId] FROM [ldr].[dbo].[AccountType] WHERE [AccountTypeName] = 'SAVINGS');
DECLARE @CreditCard UNIQUEIDENTIFIER = (SELECT [AccountTypeId] FROM [ldr].[dbo].[AccountType] WHERE [AccountTypeName] = 'CREDIT CARD');
DECLARE @Venmo UNIQUEIDENTIFIER = (SELECT [AccountTypeId] FROM [ldr].[dbo].[AccountType] WHERE [AccountTypeName] = 'VENMO');
DECLARE @PayPal UNIQUEIDENTIFIER = (SELECT [AccountTypeId] FROM [ldr].[dbo].[AccountType] WHERE [AccountTypeName] = 'PAYPAL');
DECLARE @Wallet UNIQUEIDENTIFIER = (SELECT [AccountTypeId] FROM [ldr].[dbo].[AccountType] WHERE [AccountTypeName] = 'WALLET');
DECLARE @CreditCardRewards UNIQUEIDENTIFIER = (SELECT [AccountTypeId] FROM [ldr].[dbo].[AccountType] WHERE [AccountTypeName] = 'CREDIT CARD REWARDS');
DECLARE @CD UNIQUEIDENTIFIER = (SELECT [AccountTypeId] FROM [ldr].[dbo].[AccountType] WHERE [AccountTypeName] = 'CD');

DECLARE @Transaction UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'TRANSACTION');
DECLARE @Check UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'CHECK');
DECLARE @ACH UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'ACH TRANSFER');
DECLARE @Wire UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'WIRE TRANSFER');
DECLARE @CashWithdrawal UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'CASH WITHDRAWAL');
DECLARE @CashDeposit UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'CASH DEPOSIT');
DECLARE @Transfer UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'TRANSFER');
DECLARE @BalanceTransfer UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'BALANCE TRANSFER');
DECLARE @CashBackEarnings UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'CASH BACK EARNINGS');
DECLARE @CashBackRedemption UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'CASH BACK REDEMPTION');
DECLARE @Cash UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'CASH');
DECLARE @BalancePayment UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'BALANCE PAYMENT');
DECLARE @Interest UNIQUEIDENTIFIER = (SELECT [MethodTypeId] FROM [ldr].[dbo].[MethodType] WHERE [MethodTypeName] = 'INTEREST')

INSERT INTO [ldr].[dbo].[AccountTypeMethodTypeTemplate] ([AccountTypeId], [MethodTypeId], [DefaultMethodName], [IsAccountTransferMethod]) VALUES
-- Checking
(@Checking, @Transaction,     'DEBIT CARD', 0),
(@Checking, @Check,           'CHECK', 0),
(@Checking, @ACH,             'ACH TRANSFER', 1),
(@Checking, @Wire,            'WIRE TRANSFER', 1),
(@Checking, @CashWithdrawal,  'CASH WITHDRAWAL', 1),
(@Checking, @CashDeposit,     'CASH DEPOSIT', 1),
(@Checking, @Interest,    	  'INTEREST', 0),

-- Savings
(@Savings, @ACH,            'ACH TRANSFER', 1),
(@Savings, @Wire,           'WIRE TRANSFER', 1),
(@Savings, @CashWithdrawal, 'CASH WITHDRAWAL', 1),
(@Savings, @CashDeposit,    'CASH DEPOSIT', 1),
(@Savings, @Interest,    	'INTEREST', 0),

-- Credit Card
(@CreditCard, @Transaction, 	'CREDIT CARD', 0),
(@CreditCard, @BalancePayment,  'BALANCE PAYMENT', 1),
(@CreditCard, @BalanceTransfer,  'BALANCE TRANSFER', 1),

-- Venmo
(@Venmo, @Transaction,     'TRANSACTION', 0),
(@Venmo, @Transfer, 'VENMO TRANSFER', 1),
(@Venmo, @BalanceTransfer,  'TRANSFER TO/FROM BANK', 1),

-- PayPal
(@PayPal, @Transaction,     'TRANSACTION', 0),
(@PayPal, @Transfer,        'PAYPAL TRANSFER', 1),
(@PayPal, @BalanceTransfer, 'TRANSFER TO/FROM BANK', 1),

-- Wallet
(@Wallet, @Cash, 'CASH TRANSACTION', 1),

-- Credit Card Rewards
(@CreditCardRewards, @CashBackEarnings,   'CASH BACK EARNINGS', 0),
(@CreditCardRewards, @CashBackRedemption, 'CASH BACK REDEMPTION', 1),

-- CD
(@CD, @ACH, 'ACH TRANSFER', 1),
(@CD, @Interest, 'INTEREST PAYMENT', 0)


/*
==================================================
IMAGE SORT STATUS
==================================================
*/

INSERT INTO [ldr].[dbo].[ImageSortStatusType] ([StatusType], [StatusName], [Description]) VALUES
('u', 'UNSORTED', 'Image has not been sorted yet'),
('s', 'SKIPPED', 'Image has been reviewed and skipped'),
('o', 'ORPHANED', 'Image is not associated with any transaction and requires further review'),
('c', 'COMPLETE', 'Image has been successfully sorted'),
('i', 'IN_PROGRESS', 'Image is currently being sorted. Means that the image belongs to another object that may or may not exist');

INSERT INTO [ldr].[dbo].[ImageContentType] ([ContentType], [Description]) VALUES
('STATEMENT', 'Image of account statement. ex. bank statement credit card statement'),
('INVOICE', 'Image of an invoice. ex. utility bill service invoice. Does not include purchase receipts or payment confirmations'),
('METHOD', 'Image of a payment method. ex. credit card bank check'),
('TRANSACTION', 'Image of a transaction. ex. purchase receipt payment confirmation and the invoice.'),
('RECEIPT', 'Image of a receipt. ex. Includes purchase confirmation but not invoicing details.'),
('ACCOUNT TRANSFER', 'Transfering between a users setup accounts.')


/*
==================================================
INVOICE
==================================================
*/

INSERT INTO [ldr].[dbo].[Invoice]
SELECT 
	NULL AS [UsersId],
	[invoice_id] AS [InvoiceId],
	[payee_id] AS [PayeeId],
	[invoice_date] AS [InvoiceDate],
	[due_date] AS [DueDate],
	[invoice_number] AS [InvoiceNumber],
	[total_amount_due] AS [Amount],
	[description] AS [Description],
	[start_date] AS [StartDate],
	[end_date] AS [EndDate],
	NULL AS [ImageId],
	CASE WHEN [notes] NOT IN ('','AUTO GENERATED INVOICE') THEN [notes] ELSE NULL END AS [AmazonPaymentMethod],
	CASE WHEN [notes] = 'AUTO GENERATED INVOICE' THEN 1 ELSE 0 END AS [IsAutoGenerated]
FROM [BudgetTool].[btl].[dbo].[invoice] AS i


/*
==================================================
INVOICE ITEM CATEGORY
==================================================
*/
INSERT INTO [ldr].[dbo].[InvoiceItemCategory]
SELECT
	[category_id] AS [CategoryId],
	[segment] AS [Segment],
	[category] AS [Category],
	[subcategory] AS [SubCategory],
	[unit] AS [Unit],
	[display_order] AS [DisplayOrder],
	[notes] AS [Description]
FROM [BudgetTool].[btl].[dbo].[invoice_item_category]

INSERT INTO [ldr].[dbo].[InvoiceItemCategory] ([CategoryId], [Segment], [Category], [SubCategory], [Unit], [DisplayOrder], [Description]) VALUES
('46FDA79F-ACA8-46EE-883C-380C74A8FEB0', 'SUMMARY', 'ACCOUNT TRANSFER', 'BALANCE', '', 80, 'Amount transferred between accounts'),
('0173E9DB-7618-42CD-9D56-680E1CB3A9CD', 'SUMMARY', 'ACCOUNT TRANSFER', 'TRANSFER FEE', '', 90, 'Fee associated with transfering balance')

/*
==================================================
INVOICE ITEM
==================================================
*/

INSERT INTO [ldr].[dbo].[InvoiceItem]
SELECT 
	[invoice_id] AS [InvoiceId],
	[item_id] AS [InvoiceItemId],
	[category_id] AS [CategoryId],
	[description] AS [Description],
	[quantity] AS [Quantity],
	[amount] AS [Amount],
	[display_order] AS [DisplayOrder],
	CASE WHEN [notes] = 'GENERATED invoice_item' THEN 1 ELSE 0 END AS [IsAutoGenerated]
FROM [BudgetTool].[btl].[dbo].[invoice_item]

/*
==================================================
METHOD
==================================================
*/


DROP TABLE IF EXISTS #MethodMap 
CREATE TABLE #MethodMap ([MethodId] uniqueidentifier, [MethodTypeId] UNIQUEIDENTIFIER)
INSERT INTO #MethodMap VALUES
('2DA0D38B-BF21-0FE9-EBA7-53A27A11DC07','0DAFA787-2D16-450E-A91D-C32B074151A8'),
('759C940F-D8B3-59D3-C569-53C3517DF98F','1EF0E2F5-4B9C-4064-B8EC-6A68CBDCEA4C'),
('21EA43AE-2EF2-4A41-9CCA-9BCD4EEE6E15','E23C9359-DFCA-41C4-BBC9-0C08E35FB57E'),
('3BDB5DEB-9660-90FB-FF72-0D9C3E2A6628','7AE4A186-62A0-46FB-9377-504A25BB2846'),
('F3467A2B-1434-8FDA-EDEC-E549604BC0F1','1E3B4612-5F2F-400B-84EC-DE06C4DD8269'),
('1B762D10-1CD0-8C63-411D-EA22E7D58D05','E23C9359-DFCA-41C4-BBC9-0C08E35FB57E'),
('5BC4642A-6A4B-6B7F-C175-8114D38EB74B','1E3B4612-5F2F-400B-84EC-DE06C4DD8269'),
('5615EE02-7B63-4DCF-8F46-E6E86B2F6C4A','7AE4A186-62A0-46FB-9377-504A25BB2846'),
('C1ED535F-FA72-CCEC-AC5C-88A207CAF240','0DAFA787-2D16-450E-A91D-C32B074151A8'),
('7CB14741-CB51-CD8D-9E72-477B271B6E4E','1E3B4612-5F2F-400B-84EC-DE06C4DD8269'),
('03451771-915D-B94A-DAF6-75B3710C92A5','76712111-DC2B-4EB4-9578-DDB2FAAA987A'),
('E4B712FC-346E-EB6E-E61C-FA0515635F35','0DAFA787-2D16-450E-A91D-C32B074151A8'),
('D5F8DC48-809C-2EB5-6A53-03C4B97791FC','1E3B4612-5F2F-400B-84EC-DE06C4DD8269'),
('D2B0454C-F957-585E-94E1-BE7738C2A2A9','7AE4A186-62A0-46FB-9377-504A25BB2846'),
('47339277-06EF-2FB1-CF3F-9CBD3B58E49E','E23C9359-DFCA-41C4-BBC9-0C08E35FB57E'),
('0A36261D-F99E-CB78-05AF-6484BE65EB08','0DAFA787-2D16-450E-A91D-C32B074151A8'),
('929F8009-547E-0553-B77A-717F11B6965C','1E3B4612-5F2F-400B-84EC-DE06C4DD8269'),
('9C6E5672-E1D1-7651-53BA-C1D649F0007E','1E3B4612-5F2F-400B-84EC-DE06C4DD8269'),
('87A937C3-A420-86C8-1E69-665E6D4C595C','47B12EE7-66F6-4AE3-8334-F5B23553E5CF'),
('41B02E69-85B0-3582-829A-05AC3D259C4E','1E3B4612-5F2F-400B-84EC-DE06C4DD8269')


;WITH CTE AS (
	SELECT 
		m.[account_id] AS [AccountId],
		m.[method_id] AS [MethodId] , 
		mm.[MethodTypeId], 
		[method_number] AS [MethodNumber]
	FROM [BudgetTool].[btl].[dbo].[method] AS m 
	JOIN #MethodMap AS mm ON m.method_id = mm.[MethodId]
)
INSERT INTO [ldr].[dbo].[Method]
SELECT 
	a.[AccountId], 
	CASE 
		WHEN mm.[MethodId] IS NULL THEN CAST(HASHBYTES('MD5', CAST(a.[AccountId] AS VARCHAR(50))+CAST(amt.[MethodTypeId] AS VARCHAR(50))) AS UNIQUEIDENTIFIER)
		ELSE mm.[MethodId]
	END AS [MethodId],
	amt.[MethodTypeId],
	CASE 
		WHEN amt.[MethodTypeId] NOT IN ('1E3B4612-5F2F-400B-84EC-DE06C4DD8269') THEN NULL
		ELSE 
			CASE 
				WHEN a.[AccountId] = '616B7B4A-2E64-3C4D-EB19-5E4EEC71BCC6' AND mt.[MethodTypeId] = '1E3B4612-5F2F-400B-84EC-DE06C4DD8269' THEN '4100 3902 6433 9361'
				ELSE mm.[MethodNumber] 
			END 
	END AS [MethodNumber],
	'Visa - '+RIGHT(
		CASE 
			WHEN amt.[MethodTypeId] NOT IN ('1E3B4612-5F2F-400B-84EC-DE06C4DD8269') THEN NULL 
			ELSE 
				CASE 
					WHEN a.[AccountId] = '616B7B4A-2E64-3C4D-EB19-5E4EEC71BCC6' AND mt.[MethodTypeId] = '1E3B4612-5F2F-400B-84EC-DE06C4DD8269' THEN '4100 3902 6433 9361'
					ELSE mm.[MethodNumber] 
				END 
		END,4) AS [AmazonPaymentMethod],
	NULL AS [ImageId]
FROM [ldr].[dbo].[Account] AS a
JOIN [ldr].[dbo].[AccountTypeMethodTypeTemplate] AS amt ON amt.[AccountTypeId] = a.[AccountTypeId]
JOIN [ldr].[dbo].[MethodType] AS mt ON mt.[MethodTypeId] = amt.[MethodTypeId]
LEFT JOIN CTE AS mm ON mm.[AccountId] = a.[AccountId] AND mm.[MethodTypeId] = mt.[MethodTypeId]


/*
==================================================
STATEMENT
==================================================
*/

INSERT INTO [ldr].[dbo].[Statement] (AccountId, StatementId, StatementDate, StartDate, EndDate, StartBalance, EndBalance)
SELECT 
	[account_id] AS [AccountId],
	[statement_id] AS [StatementId],
	[statement_date] AS [StatementDate],
	[period_start] AS [StartDate],
	[period_end] AS [EndDate],
	[period_start_balance] AS [StartBalance],
	[period_end_balance] AS [EndBalance]
FROM [BudgetTool].[btl].[dbo].[statement] AS s

/*
==================================================
STATEMENT ITEM
==================================================
*/

DROP TABLE IF EXISTS  ##StatementItemMethodMap
CREATE TABLE ##StatementItemMethodMap (
	StatementItemId UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
	MethodId UNIQUEIDENTIFIER NOT NULL
)

INSERT INTO ##StatementItemMethodMap SELECT transaction_id, method_id FROM [BudgetTool].[btl].[dbo].[v_statement_item] WHERE method_id = 'F3467A2B-1434-8FDA-EDEC-E549604BC0F1'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, method_id FROM [BudgetTool].[btl].[dbo].[v_statement_item] WHERE method_id = '3BDB5DEB-9660-90FB-FF72-0D9C3E2A6628'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '66ED715D-A933-F473-DB0F-299AFB26E7D9' FROM [BudgetTool].[btl].[dbo].[v_statement_item] AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE payee_type = 'account' and method_id = '47339277-06EF-2FB1-CF3F-9CBD3B58E49E'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, 'BD9AA3A7-7CAC-EE1B-6947-28BE61B19E1F' FROM [BudgetTool].[btl].[dbo].[v_statement_item] AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE payee_type = 'organization' and method_id = '47339277-06EF-2FB1-CF3F-9CBD3B58E49E'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '47339277-06EF-2FB1-CF3F-9CBD3B58E49E' FROM [BudgetTool].[btl].[dbo].[v_statement_item] AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE payee_type = 'person' and method_id = '47339277-06EF-2FB1-CF3F-9CBD3B58E49E'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '03451771-915D-B94A-DAF6-75B3710C92A5' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi WHERE  method_id = '03451771-915D-B94A-DAF6-75B3710C92A5'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, 'D5F8DC48-809C-2EB5-6A53-03C4B97791FC' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi WHERE  method_id = 'D5F8DC48-809C-2EB5-6A53-03C4B97791FC'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, 'D2B0454C-F957-585E-94E1-BE7738C2A2A9' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi WHERE  method_id = 'D2B0454C-F957-585E-94E1-BE7738C2A2A9'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '2DA0D38B-BF21-0FE9-EBA7-53A27A11DC07' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE payee_type = 'account' and vp.payee_name <> 'USACASH' and method_id = '2DA0D38B-BF21-0FE9-EBA7-53A27A11DC07'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '650CFC0F-806E-D218-E0AA-548025C3DDA9' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE payee_type = 'account' and vp.payee_name = 'USACASH' and method_id = '2DA0D38B-BF21-0FE9-EBA7-53A27A11DC07'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, 'C04D7693-2CC4-F574-D1B2-DCE45DF4D477' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE payee_type = 'organization' and method_id = '2DA0D38B-BF21-0FE9-EBA7-53A27A11DC07'

INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '1B762D10-1CD0-8C63-411D-EA22E7D58D05' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi WHERE payee_name = 'VENMONOAH' and method_id = '1B762D10-1CD0-8C63-411D-EA22E7D58D05'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '1B762D10-1CD0-8C63-411D-EA22E7D58D05' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE payee_type = 'person' and method_id = '1B762D10-1CD0-8C63-411D-EA22E7D58D05'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '1B762D10-1CD0-8C63-411D-EA22E7D58D05' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE vp.payee_name = 'HANNAH TILANDER' and method_id = '1B762D10-1CD0-8C63-411D-EA22E7D58D05'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '1B762D10-1CD0-8C63-411D-EA22E7D58D05' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE vp.payee_name = 'DAWN DIXON' and method_id = '1B762D10-1CD0-8C63-411D-EA22E7D58D05'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '23EC8F13-12CC-8EBF-1092-E02A1C90BC2A' FROM [BudgetTool].[btl].[dbo].v_statement_item WHERE transaction_id = '31036484-105B-4560-18C8-B7205F1B29F8'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '2ABE3226-3B3D-C3BB-9532-8D49B3C481CB' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE vp.payee_name = 'SECUCHECKING44153121' and method_id = '1B762D10-1CD0-8C63-411D-EA22E7D58D05'

INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '21EA43AE-2EF2-4A41-9CCA-9BCD4EEE6E15' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE payee_type = 'person' and method_id = '21EA43AE-2EF2-4A41-9CCA-9BCD4EEE6E15'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '21EA43AE-2EF2-4A41-9CCA-9BCD4EEE6E15' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE payee_type = 'account' and method_id = '21EA43AE-2EF2-4A41-9CCA-9BCD4EEE6E15'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '21EA43AE-2EF2-4A41-9CCA-9BCD4EEE6E15' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE vp.payee_name = 'NICHOLAS WHITMER' and method_id = '21EA43AE-2EF2-4A41-9CCA-9BCD4EEE6E15'

INSERT INTO ##StatementItemMethodMap SELECT transaction_id, 'CF42C730-FC87-98E8-7C47-6C3BE1489AB1' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE payee_type = 'organization' and vp.payee_name != 'NICHOLAS WHITMER' and method_id = '21EA43AE-2EF2-4A41-9CCA-9BCD4EEE6E15'

INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '6E9F9554-6AA6-725B-4566-2D887E8B6603' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id WHERE vp.payee_name = 'WELLS FARGO' and method_id = '759C940F-D8B3-59D3-C569-53C3517DF98F'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '759C940F-D8B3-59D3-C569-53C3517DF98F' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].[v_payee] AS vp ON vp.payee_id =  vsi.payee_id  WHERE payee_type = 'account'  and method_id = '759C940F-D8B3-59D3-C569-53C3517DF98F'

INSERT INTO ##StatementItemMethodMap SELECT '341CC941-E218-5421-2B12-77C75EDBF8B0', '91D41A43-6A7F-3D23-6E4A-46193665BE32' 
INSERT INTO ##StatementItemMethodMap SELECT '7E0D675F-8370-68A2-4746-CF8807519E83', '91D41A43-6A7F-3D23-6E4A-46193665BE32' 
INSERT INTO ##StatementItemMethodMap SELECT 'C049094F-B6D8-AA97-D754-AD7C0D939F78', '91D41A43-6A7F-3D23-6E4A-46193665BE32' 

INSERT INTO ##StatementItemMethodMap SELECT '5B8A0150-A268-B99D-D553-9F4D1299392B', 'FDBFCE89-EA23-49F3-02E5-16124D3706E3'
INSERT INTO ##StatementItemMethodMap SELECT '120CBED8-63E4-293C-86EF-3D8C1836EFA6', 'FDBFCE89-EA23-49F3-02E5-16124D3706E3' 

INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '2732B1B2-C215-7845-B2CC-FEA5600FDB55' FROM [BudgetTool].[btl].[dbo].v_statement_item where description = 'Interest Payment'  and method_id = 'C1ED535F-FA72-CCEC-AC5C-88A207CAF240'

INSERT INTO ##StatementItemMethodMap SELECT transaction_id, 'C1ED535F-FA72-CCEC-AC5C-88A207CAF240' FROM [BudgetTool].[btl].[dbo].v_statement_item where method_id = 'C1ED535F-FA72-CCEC-AC5C-88A207CAF240' and  transaction_id not in (Select StatementItemId FROM ##StatementItemMethodMap)


INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '604D35CF-5659-9784-595B-40FC6897FA90' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].v_payee AS vp ON vp.payee_id =  vsi.payee_id  WHERE vp.payee_name = 'WELLSFARGOSAVINGS1810566578'  and method_id = '87A937C3-A420-86C8-1E69-665E6D4C595C'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '87A937C3-A420-86C8-1E69-665E6D4C595C' FROM [BudgetTool].[btl].[dbo].v_statement_item AS vsi LEFT JOIN [BudgetTool].[btl].[dbo].v_payee AS vp ON vp.payee_id =  vsi.payee_id  WHERE vp.payee_name = 'WELLS FARGO' and method_id = '87A937C3-A420-86C8-1E69-665E6D4C595C'

INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '7CB14741-CB51-CD8D-9E72-477B271B6E4E' 
FROM [BudgetTool].[btl].[dbo].v_statement_item 
WHERE method_id IN ('7CB14741-CB51-CD8D-9E72-477B271B6E4E','9C6E5672-E1D1-7651-53BA-C1D649F0007E') AND payee_name IN (
'999 OR LESS',
'ACE HARDWARE',
'AERIE',
'ALDI',
'ALIEN JAVA',
'AMAZON',
'AMERICAN EAGLE',
'BAGELS ON POINTE',
'BAR VIRGILE',
'BATH AND BODY WORKS',
'BEAN TRADERS',
'BEE SWEET',
'BEST ITALIAN GATLINBURG',
'BOOK OF THE MONTH',
'BP',
'BRUS PUBLIC HOUSE',
'BUCEES',
'BURGWIN-WRIGHT',
'BUSCH GARDENS',
'CAMP COFFEE',
'CHAMPION',
'CHANDLER',
'CHICK FIL A',
'CHUBBYS TACOS',
'CINMARK',
'COLUMBIA',
'COMFRT',
'COSTCO',
'CUGINO FORNO',
'CVS',
'DAYTONA INTERNATIONAL SPEEDWAY',
'DGX WILMINGTON',
'DOC BS',
'DOLLAR TREE',
'DRIFT',
'VERA BRADLEY',
'WAKE COUNTY',
'WALMART',
'WAVERIDERS',
'WEGMANS',
'WENDYS',
'WHALEBONE',
'WHITE STREET BREWING',
'WHOLE FOODS',
'DUNKIN',
'DURHAM BULLS',
'DUTCH BROS',
'EARLY BIRD DOUNUTS',
'EASTCUT',
'ELITE NAIL SPA',
'ETSY',
'EXXON',
'FATBOYZ',
'FISH HEADS',
'FL COFFEE',
'FLEET FEET',
'FLUFFYS DOUGHNUTS',
'FOOD LION',
'FOXTAIL COFFEE',
'GOATS ON THE ROOF',
'GOODBERRYS',
'GRANDFATHER MOUNTAIN',
'GREYS TAVERN',
'GRITS GRILL',
'GUGLHUPF',
'HARRIS TEETER',
'HIDDEN GROUNDS',
'HOBBY LOBBY',
'HOMEGOODS',
'IKEA',
'IPSY',
'JAVA DOG COFFEE',
'JAVVY',
'JM PRODUCE',
'JOHN THE GREEK',
'LIDL',
'LODGE',
'LOWES',
'MANIFEST PHARMACY',
'MAPLEVIEW ICE CREAM',
'MARGARITAVILLE ISLAND',
'MARTINSVILLE SPEEDWAY',
'MOES',
'MY FATHERS PIZZA',
'NAGOS INC',
'NC BATTLESHIP',
'NC STATE FAIR',
'NEW HANOVER COUNTY',
'NORA CAFE',
'OBER MOUNTAIN',
'OCRACOKE ICE CREAM',
'OLD NAVY',
'OLE SMOKEY DISTILLARY',
'OOFOS',
'PALMETTO MOON',
'PEPSI',
'PERFECT EYEBROWS',
'PERFORMING ARTS RALEIGH',
'PUBLIX',
'RDC MARATHON',
'REBELLION',
'RED DRUM GRILL',
'REFUEL',
'ROYAL FARMS',
'SAN JOSE TACOS',
'SANTILLOS',
'SCOOTERS COFFEE',
'SCOTCH BONNET',
'SHEETZ',
'SHELL',
'SKINNY MIXES',
'SKYLIFT',
'SNAPCHAT',
'SNAPPY LUBE',
'SOUTH COFFEE',
'SPOTIFY',
'SPROUTS',
'STARBUCKS',
'SUNLINER DINER',
'SWEET FROG',
'TARGET',
'THE FLYING BISCUIT',
'THE HIBERNIAN',
'THE SALTY DOG',
'TJ MAXX',
'TOBACCO WOOD BREWING',
'TOTAL WINE',
'TRIANGLE CINEMAS',
'TWEETSIE RAILROAD',
'UNDER ARMOR',
'DUKE HEALTH',
'UPS',
'USPS'
)


INSERT INTO ##StatementItemMethodMap VALUES 
('14A235EA-9EF8-4758-86CE-0ECEB3B74873','7CB14741-CB51-CD8D-9E72-477B271B6E4E'),
('1DECDDC1-C0E5-98DD-DBD8-4EAA21792C35','7CB14741-CB51-CD8D-9E72-477B271B6E4E'),
('CF1CB52A-CAD6-578B-FA15-10FB2A6FE477','7CB14741-CB51-CD8D-9E72-477B271B6E4E'),
('5D8E5691-E1EA-E2F9-C47F-379D9CB2EC81','7CB14741-CB51-CD8D-9E72-477B271B6E4E'),
('B69A6FD7-41C1-925A-6EB3-9B44D03876E1','7CB14741-CB51-CD8D-9E72-477B271B6E4E'),
('BC84156B-8AC0-3720-60F6-A96F2B22D70A','7CB14741-CB51-CD8D-9E72-477B271B6E4E'),
('3A6A9664-8B7A-9C5C-5E2E-61F65ED384CC','7CB14741-CB51-CD8D-9E72-477B271B6E4E'),
('992669CC-2791-81C0-255A-7598D73F6E49','7CB14741-CB51-CD8D-9E72-477B271B6E4E'),
('139BA157-A325-AEC8-7C4F-EBA5E929566B','7CB14741-CB51-CD8D-9E72-477B271B6E4E'),
('7C978084-F47A-2699-713C-81D2D34BC8D0','7CB14741-CB51-CD8D-9E72-477B271B6E4E')

INSERT INTO ##StatementItemMethodMap SELECT transaction_id, 'E4B712FC-346E-EB6E-E61C-FA0515635F35' FROM [BudgetTool].[btl].[dbo].v_statement_item WHERE method_id IN ('7CB14741-CB51-CD8D-9E72-477B271B6E4E','E4B712FC-346E-EB6E-E61C-FA0515635F35')  AND payee_name  IN ('DUKE UNIVERSITY','CITICREDIT','SECUCREDIT4046571150920401','SECUSHARE60559787','VENMOCLAIREccmiller123')
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, 'E4B712FC-346E-EB6E-E61C-FA0515635F35' FROM [BudgetTool].[btl].[dbo].v_statement_item WHERE method_id IN ('7CB14741-CB51-CD8D-9E72-477B271B6E4E','E4B712FC-346E-EB6E-E61C-FA0515635F35') AND description  = 'SECU FOUNDATION'

INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '03451771-915D-B94A-DAF6-75B3710C92A5' FROM [BudgetTool].[btl].[dbo].v_statement_item WHERE method_id = '7CB14741-CB51-CD8D-9E72-477B271B6E4E' AND description  = 'Withdrawal or Check'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, 'E4B712FC-346E-EB6E-E61C-FA0515635F35' FROM [BudgetTool].[btl].[dbo].v_statement_item WHERE method_id = '7CB14741-CB51-CD8D-9E72-477B271B6E4E' AND description like 'DoughBoyHS6221%'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '3E87FFA6-F3A9-1F3A-3156-B9109628A6D1' FROM [BudgetTool].[btl].[dbo].v_statement_item WHERE method_id IN ('7CB14741-CB51-CD8D-9E72-477B271B6E4E','E4B712FC-346E-EB6E-E61C-FA0515635F35') AND description like 'DIVIDEND EARNED%'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '6F1449BB-9A5F-0077-B26C-D8C168AC7508' FROM [BudgetTool].[btl].[dbo].v_statement_item WHERE method_id = 'E4B712FC-346E-EB6E-E61C-FA0515635F35'  AND payee_name  ='USACASH'

INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '0A36261D-F99E-CB78-05AF-6484BE65EB08' FROM [BudgetTool].[btl].[dbo].v_statement_item WHERE method_id IN ('9C6E5672-E1D1-7651-53BA-C1D649F0007E', '0A36261D-F99E-CB78-05AF-6484BE65EB08')  AND payee_name  ='WELLS FARGO'

INSERT INTO ##StatementItemMethodMap
SELECT transaction_id, '9C6E5672-E1D1-7651-53BA-C1D649F0007E' 
FROM [BudgetTool].[btl].[dbo].v_statement_item 
WHERE method_id = '9C6E5672-E1D1-7651-53BA-C1D649F0007E' AND(transaction_id = '7639BD8C-13A5-DA20-E259-1AF6EEF86163' OR payee_name IN (
	'ADVANCE AUTO PARTS',
	'ALPACA',
	'AMERICAN MUSCLE',
	'ANDYS FROZEN CUSTARD',
	'ANTHROPOLOGIE',
	'AUTOZONE',
	'BARNS AND NOBLE',
	'BBS CRISPY CHICKEN',
	'BELK',
	'BISCUITVILLE',
	'BLACK AND WHITE',
	'BLACKSTONE',
	'BRITECO',
	'CARIBOU COFFEE',
	'CHIPOTLE',
	'CIRCLE K',
	'COMMON GROUNDS',
	'COOK OUT',
	'CUP A JOE',
	'DOLLAR GENERAL',
	'EBAY',
	'ENBRIDGE',
	'FOSTER STREET COFFEE',
	'GEORGES PIZZARIA',
	'GIRL SCOUTS',
	'OPEN AI',
	'NASCAR',
	'NOVANT',
	'NOTES COFFEE',
	'MICROSOFT',
	'ZAXBYS',
	'WILLIAMS SONOMA',
	'WHISK AND RYE',
	'WALGREENS',
	'WAKE FOREST COFFEE COMPANY',
	'VENDING MACHINE',
	'ULTA',
	'UHAUL',
	'UBER',
	'GOOGLE',
	'HAAGEN DAZS',
	'HABITAT FOR HUMANITY',
	'HAYMAKER',
	'HSP WASH',
	'KOHLS',
	'LAST PASS',
	'MACKEYS FERRY',
	'MOUNTAIN BEVERAGE',
	'NC DMV',
	'PONYSAURUS',
	'PARKMOBILE',
	'POTTERY BARN',
	'RACELAB',
	'RISE',
	'ROCK AUTO',
	'ROSECOMB',
	'SIMMONS TRUCK',
	'SPECTRUM',
	'STATE OF NC',
	'SUNGLASSES HUT',
	'SUSHI IWA',
	'SWEET SPOT ICE CREAM',
	'TAZIKIS',
	'THE FEDERAL',
	'THE HIBERNIAN PUB',
	'THE MELTING POT',
	'TICKET MASTER',
	'TOWN HALL BURGER',
	'TRADER JOES',
	'TRIANGLE COFFEE HOUSE',
	'TURBOTAX'
))

INSERT INTO ##StatementItemMethodMap VALUES ('26C37170-C144-A28F-532B-1DE22F89F8BC','D686509E-39B9-65C1-5030-8A30D8773EE9')
INSERT INTO ##StatementItemMethodMap VALUES ('BC247274-C08B-C361-0849-B0A83988D568','C7B3BD37-035A-D59D-3266-98E4E3243A16')
INSERT INTO ##StatementItemMethodMap VALUES ('756B7393-B64C-8B7A-835D-64E7FADE8F62','9A71E0A1-731C-ADC7-BD25-05EB41190780')


INSERT INTO ##StatementItemMethodMap 
SELECT transaction_id, '0A36261D-F99E-CB78-05AF-6484BE65EB08'
FROM [BudgetTool].[btl].[dbo].v_statement_item WHERE method_id = '0A36261D-F99E-CB78-05AF-6484BE65EB08' AND payee_name IN (
	'CHANDLER',
	'EBAY',
	'IRS',
	'RACELAB',
	'STATE OF NC',
	'WELLSFARGOSAVINGS1810566578',
	'VENMONOAH',
	'PAYPALNOAH'
)

INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '5BC4642A-6A4B-6B7F-C175-8114D38EB74B' FROM [BudgetTool].[btl].[dbo].v_statement_item WHERE method_id = '5BC4642A-6A4B-6B7F-C175-8114D38EB74B'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '5615EE02-7B63-4DCF-8F46-E6E86B2F6C4A' FROM [BudgetTool].[btl].[dbo].v_statement_item WHERE payee_name IN ('WELLSFARGOSAVINGS1810566578','WELLSFARGOREWARDS60022716268') and method_id = '5615EE02-7B63-4DCF-8F46-E6E86B2F6C4A'
INSERT INTO ##StatementItemMethodMap SELECT transaction_id, '9CC7252A-CB2F-0613-DE95-08D199303D63' FROM [BudgetTool].[btl].[dbo].v_statement_item WHERE payee_name IN ('PAYPALNOAH') and method_id = '5615EE02-7B63-4DCF-8F46-E6E86B2F6C4A'
INSERT INTO ##StatementItemMethodMap VALUES ('1FDA5986-3ABF-EC0C-F35F-72616A7A4CE6', '5615EE02-7B63-4DCF-8F46-E6E86B2F6C4A')


INSERT INTO [ldr].[dbo].[StatementItem]
SELECT 
	[statement_id] AS [StatementId],
	[transaction_id] AS [StatementItemId],
	smm.[MethodId] AS [MethodId],
	[payee_id] AS [PayeeId],
	[invoice_id] AS [InvoiceId],
	[transaction_date] AS [TransactionDate],
	[post_date] AS [PostDate],
	[reference_number] AS [ReferenceNumber],
	[amount] AS [Amount],
	[description] AS [Description],
	NULL AS [ImageId]
FROM [BudgetTool].[btl].[dbo].[statement_item] AS si
LEFT JOIN [BudgetTool].[btl].[dbo].[statement] AS s ON s.[account_id] = si.[account_id] and s.[statement_date] = si.[statement_date]
LEFT JOIN ##StatementItemMethodMap AS smm ON smm.[StatementItemId] = si.[transaction_id]


/*
==================================================
INVOICE TEMPLATE
==================================================
*/

INSERT INTO [ldr].[dbo].[InvoiceTemplate]
SELECT 
	[invoice_template_id] AS [InvoiceTemplateId],
	[invoice_template_name] AS [InvoiceTemplateName]
FROM [BudgetTool].[btl].[dbo].[invoice_template]

INSERT INTO [ldr].[dbo].[InvoiceTemplateItem]
SELECT 
	[invoice_template_id] AS [InvoiceTemplateId],
	[invoice_template_item_id] AS [InvoiceTemplateItemId],
	[category_id] AS [CategoryId],
	[description] AS [Description],
	[quantity] AS [Quantity],
	[amount] AS [Amount],
	[display_order] AS [DisplayOrder]
FROM [BudgetTool].[btl].[dbo].[invoice_template_item]
