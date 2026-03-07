# Data Engineering Task — Lead Pipeline

Submission for the Data Engineering Task: Excel → SQL Server → Snowflake (ADF) → LeadEvents (Python).

---

## What Was Built

| Step | Component | Description |
|------|-----------|-------------|
| 1 | SQL Server | Database, Leads table, 100 rows from Excel |
| 2 | Azure Data Factory | Incremental pipeline SQL → Snowflake (30-min trigger) |
| 3 | Snowflake | Warehouse, database, Leads & LeadEvents tables |
| 4 | Python | Transformation: Leads → LeadEvents |

---

## Project Structure

```
├── sql/              # SQL Server scripts
├── snowflake/        # Snowflake scripts
├── adf/              # ADF pipeline, datasets, linked services
├── scripts/          # Python: load_leads_to_sql, transform_leads_to_leadevents, setup_adf_config
├── .env.example      # Template for credentials
└── requirements.txt
```

---

## Quick Start

1. Copy `.env.example` to `.env` and add your credentials
2. Run `python scripts/load_leads_to_sql.py` (requires SQL Server with data)
3. Deploy ADF pipeline (configure linked services with your SQL/Snowflake/Blob)
4. Run `python scripts/transform_leads_to_leadevents.py` for LeadEvents

---

## Screenshots

*Add your screenshots below (e.g. ADF pipeline run, Snowflake data, LeadEvents output)*

### Pipeline Run (ADF)
<!-- ![ADF Pipeline Success](screenshots/adf-pipeline.png) -->

### Snowflake — Leads Table
<!-- ![Snowflake Leads](screenshots/snowflake-leads.png) -->

### Snowflake — LeadEvents Table
<!-- ![Snowflake LeadEvents](screenshots/snowflake-leadevents.png) -->

---

*Detailed setup: see `docs/` folder (local only, not in repo)*
