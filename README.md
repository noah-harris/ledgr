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
- **Audit Trail** — Database-level triggers on core tables for insert and delete events

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
├── client/                  # Desktop application
│   ├── app.py               # Main entry point
│   ├── data.py              # Data access functions
│   ├── db.py                # Database connection pool
│   ├── models/              # Domain models (Invoice, Image, StatementItem)
│   ├── tools/               # Feature modules
│   │   ├── account_creator/
│   │   ├── statement_loader/
│   │   ├── statement_viewer/
│   │   ├── invoice_manager/
│   │   ├── image_linker/
│   │   ├── transaction_linker/
│   │   ├── organization_creator/
│   │   └── users_creator/
│   └── gui/                 # Shared UI components (forms, tables, styling)
│
├── db-init/                 # Database schema deployment (runs in Docker)
│   ├── deploy.py            # Deployment orchestration script
│   ├── Tables/              # Table definitions (T-SQL)
│   ├── Views/               # View definitions
│   └── Programmability/     # Stored procedures, functions, triggers
│
├── db-seed/                 # Sample data for local development
│   ├── seed.py
│   └── SeedDataInsert.sql
│
├── shared/                  # Cross-module utilities
│   ├── config.py
│   └── db.py
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

All primary keys use `UNIQUEIDENTIFIER` (GUID). The schema includes insert and audit triggers on core tables, and a scalar function `fn_StripNonAlphanumeric` for data normalization. Views are provided for both display and DML operations.

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.12+
- [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### 1. Configure environment

Create a `.env` file in the project root with the following values:

```env
DOCKER_DB_IP=db
DOCKER_DB_INTERNAL_PORT=1433
DOCKER_DB_EXTERNAL_PORT=1434
DOCKER_DB_USERNAME=sa
DOCKER_DB_PASSWORD=

IMAGE_DIRECTORY_LOCATION=
```

| Variable | Description |
|---|---|
| `DOCKER_DB_IP` | Hostname of the SQL Server container. Use `db` when connecting from inside Docker, or `127.0.0.1` from the host machine. |
| `DOCKER_DB_INTERNAL_PORT` | Port SQL Server listens on inside the container (default `1433`). |
| `DOCKER_DB_EXTERNAL_PORT` | Port exposed to the host machine. Used by the desktop client to connect. |
| `DOCKER_DB_USERNAME` | SQL Server login username. |
| `DOCKER_DB_PASSWORD` | SQL Server login password. |
| `IMAGE_DIRECTORY_LOCATION` | Base URL of the image/document file server. Used to fetch and register documents in the Image table. |

### 2. Start the database and deploy the schema

```powershell
./start_db.ps1
```

This builds the Docker images, starts SQL Server, waits for it to become healthy, then automatically runs the `db-init` container to deploy the full database schema.

To also load sample data:

```powershell
./start_db_seed_data.ps1
```

### 3. Launch the application

In a separate terminal:

```powershell
./start_client.ps1
```

This installs Python dependencies and launches the Tkinter desktop GUI.

### 4. Stop the database

```powershell
./stop_db.ps1
```

This saves a restore point before bringing the containers down.

---

## Data Seeding

`seed.py` is the Docker Compose entry point for the `db-seed` service. When run, it attempts to import and execute `local.py`. If `local.py` is not present, it does nothing. This keeps all environment-specific seeding logic out of source control — `local.py` is created locally per machine and never committed.

---

## License

This project is for personal and portfolio use.
