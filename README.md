# ledgr

A full-stack personal finance and invoicing desktop application built with Python, Tkinter, and Microsoft SQL Server — containerized with Docker for consistent, reproducible deployment.

---

## Overview

Ledgr is a desktop application for managing personal finances, bank statements, and invoices. It provides a structured workflow for importing bank statement data, categorizing transactions, creating and tracking invoices, and managing supporting documents (PDFs, images). The database layer runs in a Docker container and is automatically deployed on startup, with schema versioning, audit triggers, and restore points built in.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Desktop GUI | Python 3.12 · Tkinter / ttk |
| Data Layer | SQLAlchemy · pandas · pyodbc |
| Database | Microsoft SQL Server (Docker) |
| Document Handling | PyMuPDF · Pillow |
| Excel Integration | pywin32 (COM automation) |
| Containerization | Docker · Docker Compose |
| Configuration | python-dotenv |
| Logging | colorlog |

---

## Features

- **Account Management** — Create and manage financial accounts tied to organizations, account types, and currencies
- **Statement Import** — Load bank statements via Excel with COM automation; view embedded images inline during import
- **Transaction Categorization** — Link statement line items to invoices and expense categories
- **Invoice Lifecycle** — Create, view, edit, and search invoices with payee tracking, line items, and payment methods
- **Invoice Templates** — Define reusable invoice templates to speed up recurring entries
- **Document Linking** — Attach PDF and image files to statements and invoices; track processing status per document
- **Organization Registry** — Maintain a registry of banks and financial institutions
- **Database Restore Points** — Timestamped automatic database backups before destructive operations

---

## Architecture

```
┌──────────────────────────────────┐
│        Tkinter Desktop GUI       │  client/app.py
│  (modular tool-based interface)  │
└────────────────┬─────────────────┘
                 │
┌────────────────▼─────────────────┐
│     Data Access Layer            │  client/data.py
│  (SQLAlchemy + pandas queries)   │
└────────────────┬─────────────────┘
                 │  pyodbc / ODBC Driver 17
┌────────────────▼─────────────────┐
│    Microsoft SQL Server          │  Docker container
│  Tables · Views · Triggers       │
│  Stored Procedures · Functions   │
└──────────────────────────────────┘
```

The application follows a three-tier architecture: a modular Tkinter GUI, a pandas-based data access layer that issues parameterized SQL queries through SQLAlchemy, and a SQL Server database running in Docker. Each GUI tool (Statement Loader, Invoice Manager, etc.) is an isolated module under `client/tools/`. The database schema is deployed automatically by a dedicated `db-init` container at startup.

---

## Project Structure

```
ledgr/
├── client/                      # Desktop application
│   ├── app.py                   # Main entry point
│   ├── data.py                  # Data access functions
│   ├── db.py                    # Database connection pool
│   ├── models/                  # Domain models (Invoice, Image, StatementItem)
│   ├── tools/                   # Feature modules
│   └── gui/                     # Shared UI components (forms, tables, styling)
│
├── database/                    
│   ├── index/                   # Table indexes
│   ├── scalar_valued_function/  # Scalar valued functions ie f(x) = x+1           
│   ├── schema/
    ├── stored_procedure/
    ├── table/
    ├── trigger/
│   └── view/     
│
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Database Schema

The schema is organized around these core entities:

| Table | Purpose |
|---|---|
| `Users` | User profiles |
| `Account` | Financial accounts (linked to users, organizations, currencies) |
| `Statement` | Bank statements with opening/closing balances |
| `StatementItem` | Individual transactions within a statement |
| `Invoice` | Invoices with payee and date tracking |
| `InvoiceItem` | Line items within invoices, categorized by expense type |
| `InvoiceTemplate` | Reusable invoice templates |
| `Image` | Document metadata (PDF/image files) with content type and status |
| `Organization` | Banks and financial institutions |
| `Payee` | Vendor/payee reference data |
| `Method` | Payment methods |
| `Budget` | Budget table dictates a budgets name + StartDate & EndDate, BudgetItem table dictates the values for the Segment, Category, SubCategory combinations |

All primary keys use `UNIQUEIDENTIFIER` (GUID). The schema includes insert and audit triggers on core tables, and a scalar function `fn_StripNonAlphanumeric` for data normalization. Views are provided for both display and DML operations.

---

### Information
#### **Users**
Currently the user system is not implemented.

#### **Account**
An account is simply something a collection of money. This could be a bank account, a wallet, a PayPal etc.

#### **Method**
An account can have many Payment Methods assigned to it. For example, an account transfer or cash deposit.

#### **Transaction**
When a "Transaction" is reffered to, it is talking about this Invoice to StatementItem relationship.

##### **Statement Item**
Statements are loaded into the database currently through the Statement Excel Tool. 

Each row in StatementItem equates to a swipe of your credit card, a transfer etc. (Each row is manually assigned a payee and a method)

##### **Invoice**
Conceptially an Invoice is a bill that needs to be paid. (A bill can be partially or fully paid and my multiple different people (Accounts)). 
Thus Invoices are a one-to-many relationship with StatementItems.

The InvoiceItem table houses the line items of the invoice. So items you purchases from the store get a seperate line item as well as tax and or any discounts.
Each row in the InvoiceItem table has an InvoiceItemCategory associated with it.

#### **Budgets**
Recall that each Invoice Item is linked to an InvoiceItemCategory, which has three levels: Segment, Category, and Subcategory.
Budgets let you set a spending target at any of these levels for a given time period.

For example, you could set a $500 target for the Groceries segment from 2026-04-01 to 2026-04-30.
Targets can also be narrowed to a Category — Groceries > Food at $400 — or down to a Subcategory, like Groceries > Food > Dairy at $40.

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.12+
- [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### 1. Configure environment

Create a `.env` file in the project root with the following values:

```env
DB_USERNAME=
DB_PASSWORD=
INTERNAL_PORT=1433
EXTERNAL_PORT=1434
DIALECT=mssql
HOST=db
SQL_PROJECT_DIRECTORY= (In my case) "//Primary-server/d/Repositories/ledgr/database"
RESTORE_POINT_DIRECTORY= (In my case) "//Primary-server/d/Repositories/!BACKUPS/ledgr"
IMAGE_DIRECTORY_LOCATION= (In my case) http://192.168.0.238:8000
RESTORE_POINT_INTERVAL_MINUTES=5
RESTORE_POINT_RETENTION=100
```

| Variable | Description |
|---|---|
| `HOST` | Hostname of the SQL Server container. Use `db` when connecting from inside Docker, or `127.0.0.1` from the host machine. |
| `INTERNAL_PORT` | Port SQL Server listens on inside the container (default `1433`). |
| `EXTERNAL_PORT` | Port exposed to the host machine. Used by the desktop client to connect. |
| `DB_USERNAME` | SQL Server login username. |
| `DB_PASSWORD` | SQL Server login password. |
| `SQL_PROJECT_DIRECTORY` | Directory of the database project files. |
| `RESTORE_POINT_DIRECTORY` | Directory that backups get saved too. |
| `IMAGE_DIRECTORY_LOCATION` | SQL Server login password. |
| `RESTORE_POINT_INTERVAL_MINUTES` | Backup interval in minutes. |
| `RESTORE_POINT_RETENTION` | How many backups are saved of the database data before they start getting culled. Note that if no data has changed, it will not create a new backup. |

### 2. Start the database and deploy the schema

```powershell
docker compose up --pull always --build
```
Builds and starts the docker container for the database and db-deployer
Make sure to rebuild and pull dependencies in case the db-deployer has been updated.


### 3. Launch the application

In a separate terminal:

```powershell
./start_client.ps1
```

This installs Python dependencies and launches the Tkinter desktop GUI.

### 4. Stopping the docker container

```powershell
docker compose down
```

Nothing fancy

## License

This project is for personal and portfolio use.
