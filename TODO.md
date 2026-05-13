1. add single source of truth for SUPPORTED_IMAGE_TYPES
2. Clean up environment variables
3. [UI Bug] Statement item card labels clip container border — ttk.Label widgets (the "View Receipt" button and left-side info text) overflow/clip the border of their parent container on the invoice viewer's invoice card. Fix padding/layout so labels stay within bounds.
4. [UI Bug] Low-contrast buttons — some buttons (light buttons on light background) do not meet contrast requirements. Audit all button styles and ensure sufficient foreground/background contrast.
5. [UI Bug] Edit/View/Delete column UX — the separate Edit and View button columns in the table are redundant and cluttered. Consolidate into a single row with one Edit button, one View button, and one Delete button. May require modifying the table class and rebinding button callbacks.
6. [UI Bug] Grey box artifact on image viewer frame — the frame containing the canvas and filename in the image viewer has an unwanted grey box. The whole frame should have padding, a visible border, and a light background color.

-- UI Polish --
7. [UI] Image sorter table — clicking a row should load the selected image into the viewer and sync the image queue position.
8. [UI] Image viewer — images should render starting from the top-left corner (currently anchored bottom-left).
9. [UI] Invoice card description section — polish layout: uppercase muted title, proper padding, larger body text, wider wraplength.
10. [UI] Invoice card layout — InvoicePanel table columns clip text; make the whole card and table stretch to fill available width.
11. [UI] Invoice card description label needs to be more polished visually.
12. [UI] Menu bar — style with PRIMARY color background and TEXT_LIGHT foreground to match app theme.
13. [UI] Window title bar color — set to PRIMARY using Win32 ctypes (DWMWA_CAPTION_COLOR, Windows 11 only).
14. [UI] App logo / icon — create .ico file and apply via self.iconbitmap() in App.

-- Features --
15. [Feature] Invoice editor — implement full edit UI (pre-fill InvoiceForm + InvoiceItemTable from existing invoice, save via data.update_invoice()).
16. [Feature] Main page dashboard — replace placeholder with panels for: Missing Statements, Account Transfer Issues, Images to Sort, Statement Items with No Invoice, Orphan Invoices, Invoice Amount Mismatches.
17. [Feature] Budget system — Budget table (name, start_date, end_date) + BudgetCategory (budget_id, category_id, target_amount). UI to create/edit budgets; compare actual invoice item spend per category vs target.
18. [Feature] Assign segments to Organizations — for each Organization without a segment classification, allow user to assign one via the OrganizationCreator UI or a seed script.

-- Refactor --
19. [Refactor] Clean up bare print() calls across client/ — replace with logger.debug() / logger.warning() as appropriate.

-- Data --
20. [Data] Add data.v_OrphanInvoices() — invoices not linked to any StatementItem.
21. [Data] Add data.v_InvoiceAmountMismatch() — invoices where Invoice.Amount ≠ sum(InvoiceItem.Amount) or ≠ StatementItem.Amount.
22. [Data] Add data.p_MissingStatementCheck() — wrapper for stored proc that detects gaps in statement coverage per account.