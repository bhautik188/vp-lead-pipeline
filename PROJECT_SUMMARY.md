# Data Engineering Task - Project Summary

## 1. Project Overview

This project implements **Step 1** of the Data Engineering Task: loading Excel lead data into SQL Server. It includes SQL scripts (for submission) and a Python script to automate the load. The solution supports 100 lead rows with duplicate Ids (same lead in different states/emails).

---

## 2. Technologies Used

### 2.1 Database
| Technology | Version | Purpose |
|------------|---------|---------|
| **Microsoft SQL Server** | 2022 | Relational database for Leads table |
| **Docker** | - | Runs SQL Server in a container (linux/amd64 image; emulates on Apple Silicon) |

### 2.2 Python
| Package | Purpose |
|---------|---------|
| **Python** | 3.13+ |
| **pandas** | Read Excel, manipulate DataFrame |
| **openpyxl** | Excel file I/O for `.xlsx` |
| **pymssql** | SQL Server driver (no unixODBC required on macOS) |
| **sqlalchemy** | Database connection and `to_sql()` |
| **python-dotenv** | Load credentials from `.env` |

---

## 3. Project Structure

```
VP Project/
├── .env                    # SQL credentials (gitignored)
├── .env.example            # Template for .env
├── .gitignore              # .env, venv/
├── Data Enginnering Task Dummy Data.xlsx   # Source data (100 leads)
├── Data_Engineering_Task.pdf              # Task specification
├── load_leads_to_sql.py    # Python: loads Excel → SQL (creates DB/table)
├── PROJECT_SUMMARY.md      # This file
├── requirements.txt        # Python dependencies
├── start_sql_server.sh     # Start SQL Server in Docker
├── venv/                   # Python virtual environment
└── sql/
    ├── 01_create_database.sql    # Creates LeadManagement database
    ├── 02_create_leads_table.sql # Creates Leads table
    └── 03_insert_leads_data.sql # INSERT statements (100 rows)
```

---

## 4. SQL Schema

### Database
- **LeadManagement**

### Leads Table

| Column | Type | Description |
|--------|------|-------------|
| RowId | INT IDENTITY(1,1) PRIMARY KEY | Surrogate key (allows duplicate Ids) |
| Id | UNIQUEIDENTIFIER NOT NULL | Lead identifier |
| State | INT NOT NULL | 0=Sold, 1=CancellationRequested, 2=Cancelled, 3=CancellationRejected |
| CreatedDateUtc | DATETIME2 | Sold date (State=0) |
| CancellationRequestDateUtc | DATETIME2 | Request date (State=1) |
| CancellationDateUtc | DATETIME2 | Confirmed date (State=2) |
| CancellationRejectionDateUtc | DATETIME2 | Rejected date (State=3) |
| SoldEmployee | NVARCHAR(255) | Email of seller |
| CancelledEmployee | NVARCHAR(255) | Email of canceller |
| UpdatedDateUtc | DATETIME2 | Last update |

**Note:** `RowId` allows multiple rows per `Id` (same lead, different state/email over time).

---

## 5. Environment Variables

Defined in `.env` (copy from `.env.example`):

| Variable | Example | Description |
|----------|---------|-------------|
| SQL_SERVER | 127.0.0.1 | SQL Server host |
| SQL_SERVER_PORT | 1433 | Port |
| SQL_DATABASE | LeadManagement | Database name |
| SQL_USER | sa | Username |
| SQL_PASSWORD | Bhautik1! | Password (must match Docker) |

---

## 6. How to Run

### 6.1 Prerequisites
- Docker Desktop installed and running
- Python 3.8+ with venv
- `.env` configured

### 6.2 Start SQL Server (Docker)
```bash
./start_sql_server.sh
# Wait ~30–60 seconds (longer on Apple Silicon)
```

### 6.3 Load Data (Python)
```bash
source venv/bin/activate
python load_leads_to_sql.py
```

The script will:
1. Connect to `master`
2. Create `LeadManagement` database if missing
3. Drop and recreate `Leads` table
4. Insert all 100 rows from Excel
5. Create `adt_watermark` table and `sp_UpdateWatermark` (for Step 2 ADF pipeline)

### 6.4 SQL Scripts (Manual / Submission)
Run via sqlcmd, Azure Data Studio, or SSMS:
1. `sql/01_create_database.sql`
2. `sql/02_create_leads_table.sql`
3. `sql/03_insert_leads_data.sql`
4. `sql/04_create_watermark_table.sql` (optional; Python does this automatically)

---

## 7. Python Script Details

### `load_leads_to_sql.py`

**Flow:**
1. `get_connection_params()` – read from `.env`
2. `load_excel_to_dataframe()` – read Excel, align `CanceledEmployee` → `CancelledEmployee`
3. `insert_leads_to_sql()`:
   - Connect to `master`, create database if needed (AUTOCOMMIT for CREATE DATABASE)
   - Connect to `LeadManagement`, drop and create `Leads` table
   - Retry connection (up to 6 attempts, 5s apart) for slow Docker startup
   - Insert via `pandas.to_sql()` (chunks of 50)

**Dependencies:** pymssql (no unixODBC on macOS)

---

## 8. Docker

**Image:** `mcr.microsoft.com/mssql/server:2022-latest`  
**Platform:** linux/amd64 (emulated on Apple Silicon)  
**Port:** 1433 → 1433  
**Password:** Must satisfy SQL Server policy (uppercase, lowercase, number, symbol)

**Note:** Use single quotes for password in shell to avoid `!` expansion.

---

## 9. Viewing Data

- **Azure Data Studio / DBeaver / TablePlus:** Connect to `localhost,1433` with `sa` and password
- **Python:**
  ```python
  import pymssql
  conn = pymssql.connect(server='127.0.0.1', port=1433, user='sa', password='Bhautik1!', database='LeadManagement')
  cur = conn.cursor()
  cur.execute('SELECT * FROM Leads')
  for row in cur.fetchall():
      print(row)
  ```

---

## 10. Data Source

- **File:** `Data Enginnering Task Dummy Data.xlsx`  
- **Rows:** 100  
- **Unique Ids:** ~80 (some leads repeat with different State/email)  
- **Columns:** Id, State, CreatedDateUtc, CancellationRequestDateUtc, CancellationDateUtc, CancellationRejectionDateUtc, CanceledEmployee, SoldEmployee, UpdatedDateUtc

---

## 11. Task PDF Alignment

| Requirement | Implementation |
|-------------|----------------|
| Create database | `01_create_database.sql` + Python |
| Create Leads table | `02_create_leads_table.sql` + Python |
| Insert Excel data | `03_insert_leads_data.sql` + `load_leads_to_sql.py` |
| Schema types | UUID→UNIQUEIDENTIFIER, Int→INT, DateTime→DATETIME2, String→NVARCHAR(255) |

---

## 12. Future Steps (per PDF)

- ~~Step 2: Azure Data Factory pipeline (SQL → Snowflake)~~ **Done** – see `adf/`
- Step 3: Snowflake setup (warehouse, database, Leads table)
- Step 4: Python transformation (Leads → LeadEvents in Snowflake)
