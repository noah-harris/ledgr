1. [Refactor] add single source of truth for SUPPORTED_IMAGE_TYPES

2. [Refactor] Clean up environment variables

3. [UI] ~~Statement item card labels clip container border — ttk.Label widgets (the "View Receipt" button and left-side info text) overflow/clip the border of their parent container on the invoice viewer's invoice card. Fix padding/layout so labels stay within bounds.~~

4. [UI] ~~Low-contrast buttons — some buttons (light buttons on light background) do not meet contrast requirements. Audit all button styles and ensure sufficient foreground/background contrast.~~

5. [UI] ~~Edit/View/Delete column UX — the separate Edit and View button columns in the table are redundant and cluttered. Consolidate into a single row with one Edit button, one View button, and one Delete button. May require modifying the table class and rebinding button callbacks.~~

6. [UI] ~~Grey box artifact on image viewer frame — the frame containing the canvas and filename in the image viewer has an unwanted grey box. The whole frame should have padding, a visible border, and a light background color.~~

-- UI Polish --
7. [UI] ~~Image sorter table — clicking a row should load the selected image into the viewer and sync the image queue position.~~ DONE
8. [UI] ~~Image viewer — images should render starting from the top-left corner (currently anchored bottom-left).~~ DONE
9. [UI] ~~Invoice card description section — polish layout: uppercase muted title, proper padding, larger body text, wider wraplength.~~
10. [UI] Invoice card layout — InvoicePanel table columns clip text; make the whole card and table stretch to fill available width.
11. [UI] ~~Invoice card description label needs to be more polished visually.~~
12. [UI] ~~Menu bar — style with PRIMARY color background and TEXT_LIGHT foreground to match app theme.~~ DONE
13. [UI] Window title bar color — set to PRIMARY using Win32 ctypes (DWMWA_CAPTION_COLOR, Windows 11 only).
14. [UI] App logo / icon — create .ico file and apply via self.iconbitmap() in App.

-- Features --
15. [Feature] Invoice editor — implement full edit UI (pre-fill InvoiceForm + InvoiceItemTable from existing invoice, save via data.update_invoice()).
16. [Feature] Main page dashboard — replace placeholder with panels for: Missing Statements, Account Transfer Issues, Images to Sort, Statement Items with No Invoice, Orphan Invoices, Invoice Amount Mismatches.
17. [Feature] Budget system — Budget table (name, start_date, end_date) + BudgetCategory (budget_id, category_id, target_amount). UI to create/edit budgets; compare actual invoice item spend per category vs target.
18. [Feature] ~~Assign segments to Organizations — for each Organization without a segment classification, allow user to assign one via the OrganizationCreator UI or a seed script.~~ DONE (OrganizationCreator now has full Organization + OrganizationType editor)

-- Refactor --
19. [Refactor] ~~Clean up bare print() calls across client/ — replace with logger.debug() / logger.warning() as appropriate.~~ DONE
24. [Refactor] Finish the implementation of the user system. The functionality is not really scoped yet other than 1, a user should not be able to see other users information, 2, if 2 users are for example married there finances are combined. THis means that not only can they see each others information, but all objects are shared so that makes the database part a little less straight forward.
This is a very large task and needs careful consideration.

23. [Refactor] Orgasnization Type needs another degree of freedom on it. Add a category column.


-- Data --
20. [Data] Add data.v_OrphanInvoices() — invoices not linked to any StatementItem.
21. [Data] Add data.v_InvoiceAmountMismatch() — invoices where Invoice.Amount ≠ sum(InvoiceItem.Amount) or ≠ StatementItem.Amount.
22. [Data] Add data.p_MissingStatementCheck() — wrapper for stored proc that detects gaps in statement coverage per account.
23a. [Data] Update the new Category column with values.
25. [Data] The invoice item category system does not necessarily need to be refactored, some of the categories just need a little more specificity.
This task is vague and needs more explenation.

26. ~~for the Invoice Item Category remapper, I would like to able to type and have it auto fill in the same way that the InvoiceItemCateogry column does in the invoiceItem table editor.~~
27. ~~In the Invoice Item Category editor, I would like to see how many line items currently exist for it in the databse~~
28. ~~I would like to the display order just automatically increment by 10 to the largest one from the segment. So if the PAYCHECK Segment has a maximum display order of 190, when a usesr createds a new PAYCHECK InvoiceItemCategory if the Display order field is empty, it becomes 200.~~

29. Add a units table

30. There is a bug where when clicking the Create statement menu button, the modal appears in the top left corner not in the center of the screen.

31. Sorting an image in image sort should remove that item form the table

32. When uploading a statement item in the statement item loaded, when clicking the load statement button it should close the window.
32a. Additionally, then statement viewer and the statement loader (UploadStatement and reopen excel) should be in the same tool