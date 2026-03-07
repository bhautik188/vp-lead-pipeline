# Data Engineering Task — Lead Pipeline

A complete data pipeline implementing **Excel → SQL Server → Snowflake (via Azure Data Factory) → LeadEvents (via Python)** for lead lifecycle management.

---

## Pipeline Overview

```
Excel (100 leads) → SQL Server (Leads) → ADF (incremental) → Snowflake (LEADS) → Python → LeadEvents
```

| Step | Component | Description |
|------|-----------|-------------|
| **1** | SQL Server | Database, Leads table, 100 rows from Excel |
| **2** | Azure Data Factory | Incremental pipeline SQL → Snowflake, trigger every 30 min |
| **3** | Snowflake | Warehouse, database, LEADS & LeadEvents tables |
| **4** | Python | Transformation: Leads → LeadEvents (event types per state) |

---

## Project Structure

*Scripts marked with ★ are explicitly required by the task PDF.*

| Task Step | Required Scripts |
|-----------|------------------|
| **Step 1 — SQL** | `01_create_database.sql`, `02_create_leads_table.sql`, `03_insert_leads_data.sql` + `load_leads_to_sql.py` (Excel → SQL) |
| **Step 2 — ADF** | `adf/` pipeline, linked services, trigger (30 min), incremental loads |
| **Step 3 — Snowflake** | `01_create_warehouse.sql`, `02_create_database.sql`, `03_create_leads_table.sql` |
| **Step 4 — Python** | `transform_leads_to_leadevents.py` (Leads → LeadEvents) + `04_create_leadevents_table.sql` |

```
├── sql/                    # Step 1: SQL Server
│   ├── 01_create_database.sql      ★ Create database
│   ├── 02_create_leads_table.sql   ★ Create Leads table
│   ├── 03_insert_leads_data.sql    ★ Insert Excel data (100 leads)
│   └── 04_create_watermark_table.sql   (ADF incremental loads) (part of step 2)
├── snowflake/              # Step 3: Snowflake
│   ├── 01_create_warehouse.sql     ★ Create warehouse
│   ├── 02_create_database.sql      ★ Create database
│   ├── 03_create_leads_table.sql   ★ Create Leads table
│   └── 04_create_leadevents_table.sql   ★ Create LeadEvents table (part of transformation task)
├── adf/                    # Step 2: Azure Data Factory
│   ├── linkedService/      ★ LsSqlServer, LsSnowflake, LsAzureBlobStaging
│   ├── dataset/            ★ DsSqlLeads, DsSnowflakeLeads, DsSqlWatermarkLookup
│   ├── pipeline/           ★ PlLeadsSqlToSnowflake (SQL → Snowflake)
│   └── trigger/            ★ TrgLeadsEvery30Min (every 30 min)
├── scripts/                # Python
│   ├── load_leads_to_sql.py        ★ Excel → SQL: reads Excel, creates DB/table, inserts 100 leads, sets up watermark for ADF
│   └── transform_leads_to_leadevents.py   ★ Leads → LeadEvents (Step 4)
├── .env.example            # Template for credentials
└── requirements.txt
```

**`load_leads_to_sql.py`** — Reads `Data Enginnering Task Dummy Data.xlsx`, creates the LeadManagement database and Leads table if missing, inserts all 100 rows, and creates the `adt_watermark` table + `sp_UpdateWatermark` stored procedure for ADF incremental loads. Uses credentials from `.env` (SQL_SERVER, SQL_USER, SQL_PASSWORD). Run this before the ADF pipeline.

---

## Prerequisites

- **Python 3.8+** with `venv`
- **SQL Server** (Azure SQL)
- **Snowflake** account
- **Azure Data Factory** with GitHub integration
- **Azure Blob Storage** (for ADF staging)

---

## Quick Start

### 1. Environment Setup

```bash
cp .env.example .env
# Edit .env with your SQL_SERVER, SQL_PASSWORD, SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD
```

### 2. Load Data to SQL

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/load_leads_to_sql.py
```

**Expected:** `Inserted 100 rows into Leads table (watermark table ready for Step 2 ADF)`

### 3. Deploy ADF Pipeline

- Connect ADF to this GitHub repo
- Configure linked services in ADF UI with your credentials:
  - **LsSqlServer** — SQL Server / Azure SQL
  - **LsSnowflake** — Snowflake account
  - **LsAzureBlobStaging** — Blob Storage (for staging)
- Run Snowflake scripts (`snowflake/*.sql`) to create warehouse, database, and tables
- Publish and trigger the pipeline

### 4. Transform to LeadEvents

```bash
python scripts/transform_leads_to_leadevents.py
```

**Expected:** LeadEvents table populated in Snowflake with event types (LeadSold, LeadCancellationRequested, LeadCancelled, LeadCancellationRejected).

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SQL_SERVER` | SQL Server host (e.g. `localhost` or `yourserver.database.windows.net`) |
| `SQL_DATABASE` | `LeadManagement` |
| `SQL_USER` | SQL username |
| `SQL_PASSWORD` | SQL password |
| `SNOWFLAKE_ACCOUNT` | Snowflake account identifier |
| `SNOWFLAKE_DATABASE` | `LEADMANAGEMENT` |
| `SNOWFLAKE_WAREHOUSE` | `LEAD_WH` |
| `SNOWFLAKE_USER` | Snowflake username |
| `SNOWFLAKE_PASSWORD` | Snowflake password |

---

## Lead Model & Transformation

**Lead states:** Sold (0), CancellationRequested (1), Cancelled (2), CancellationRejected (3)

**LeadEvents mapping:**

| State | EventType | EventEmployee | EventDate |
|-------|-----------|---------------|-----------|
| 0 | LeadSold | SoldEmployee | CreatedDateUtc |
| 1 | LeadCancellationRequested | Unknown | CancellationRequestDateUtc |
| 2 | LeadCancelled | CancelledEmployee | CancellationDateUtc |
| 3 | LeadCancellationRejected | Unknown | CancellationRejectionDateUtc |

---

## Screenshots

See [SCREENSHOTS.md](SCREENSHOTS.md) for pipeline, ADF, Snowflake, and LeadEvents screenshots.

---

