# Setup and Run — Step-by-Step Guide

Follow these steps **in order** to complete the data pipeline (SQL → Snowflake via Azure Data Factory).

---

## Prerequisites

- **SQL:** Docker (local) **or** Azure SQL Database (recommended for Mac)
- **Python 3.8+** — with `venv` created and packages installed  
- **Azure account** — for Data Factory  
- **Snowflake account** — [free trial](https://signup.snowflake.com)

**Mac users:** See [docs/AZURE_SQL_SETUP.md](docs/AZURE_SQL_SETUP.md) for Azure SQL — no Docker or Self-hosted IR needed.

---

## Part A: Create SQL Resources (Task Step 1)

### A1. Start SQL Server

```bash
./start_sql_server.sh
```

Wait about 30 seconds for the container to start.

---

### A2. Load Excel data into SQL

```bash
source venv/bin/activate
python load_leads_to_sql.py
```

**Expected output:** `Inserted 100 rows into Leads table (watermark table ready for Step 2 ADF)`

This script will:

- Create the `LeadManagement` database (if it doesn’t exist)  
- Create the `Leads` table  
- Insert all 100 rows from the Excel file  
- Create the `adt_watermark` table and `sp_UpdateWatermark` stored procedure (for incremental loads)

---

### A3. Verify (optional)

Connect to `localhost:1433` with `sa` / your password and run:

```sql
USE LeadManagement;
SELECT COUNT(*) FROM Leads;        -- should return 100
SELECT * FROM adt_watermark;       -- should show one row for 'Leads'
```

---

## Part B: Create Snowflake Resources (Task Step 3)

Step 2 (ADF pipeline) copies into Snowflake. Snowflake must have the warehouse, database, and `LEADS` table before the pipeline runs.

### B1. Open Snowflake

1. Go to [app.snowflake.com](https://app.snowflake.com) (or your Snowflake URL, e.g. `https://your-account.region.snowflakecomputing.com`)
2. Log in with your Snowflake username and password
3. In the left sidebar, click **Projects** → **Worksheets**
4. Click **+ Worksheet** to open a new worksheet
5. The worksheet is where you run the SQL in B2–B4. **Important:** Select only the SQL code (not the headings or instructions), then click **Run** (▶) or press **Ctrl+Enter** (Windows) / **Cmd+Enter** (Mac). Run each block (B2, B3, B4) separately.

---

### B2. Create warehouse

1. **Select** (click and drag to highlight) only this SQL:

```sql
CREATE WAREHOUSE IF NOT EXISTS LEAD_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;
```

2. **Run** it: click **Run** (▶) or press **Ctrl+Enter** (Windows) / **Cmd+Enter** (Mac).

3. **Check**: In the results area below, you should see `Warehouse LEAD_WH successfully created` (or `already exists`).

---

### B3. Create database

1. **Select** (highlight) only this SQL:

```sql
CREATE DATABASE IF NOT EXISTS LEADMANAGEMENT;
USE DATABASE LEADMANAGEMENT;
USE WAREHOUSE LEAD_WH;
```

2. **Run** it: **Run** (▶) or **Ctrl+Enter** / **Cmd+Enter**.

3. **Check**: You should see success messages. In Database Explorer (left), expand to confirm `LEADMANAGEMENT` appears.

---

### B4. Create Leads table

1. **Select** (highlight) only this SQL:

```sql
USE DATABASE LEADMANAGEMENT;
USE WAREHOUSE LEAD_WH;
USE SCHEMA PUBLIC;

CREATE TABLE IF NOT EXISTS LEADS (
    ROWID INTEGER,
    ID VARCHAR(36) NOT NULL,
    STATE INTEGER NOT NULL,
    CREATEDDATEUTC TIMESTAMP_NTZ,
    CANCELLATIONREQUESTDATEUTC TIMESTAMP_NTZ,
    CANCELLATIONDATEUTC TIMESTAMP_NTZ,
    CANCELLATIONREJECTIONDATEUTC TIMESTAMP_NTZ,
    SOLDEMPLOYEE VARCHAR(255),
    CANCELLEDEMPLOYEE VARCHAR(255),
    UPDATEDDATEUTC TIMESTAMP_NTZ
);
```

2. **Run** it: **Run** (▶) or **Ctrl+Enter** / **Cmd+Enter**.

3. **Check**: Results should show `Table LEADS successfully created`. In Database Explorer: **LEADMANAGEMENT** → **PUBLIC** → **Tables** → **LEADS**.

---

## Part C: Configure Credentials

### C1. Check SQL credentials in `.env`

Your `.env` should include (values already used when you ran `load_leads_to_sql.py`):

```
SQL_SERVER=localhost
SQL_SERVER_PORT=1433
SQL_DATABASE=LeadManagement
SQL_USER=sa
SQL_PASSWORD=your-actual-password
```

---

### C2. Add credentials to `.env`

**For local SQL Server (used by ADF):** Add the name of your Self-hosted Integration Runtime:
```
SELF_HOSTED_IR_NAME=SelfHostedIR
```
Replace `SelfHostedIR` with the exact name you give the Self-hosted IR in ADF (E3). This makes the generated `LsSqlServer.json` use the correct runtime.

Add these lines (replace with your real values):

```
SNOWFLAKE_ACCOUNT=xy12345.eu-west-1
SNOWFLAKE_DATABASE=LEADMANAGEMENT
SNOWFLAKE_WAREHOUSE=LEAD_WH
SNOWFLAKE_USER=your-snowflake-username
SNOWFLAKE_PASSWORD=your-snowflake-password
```

**Finding your account identifier:**  
If your Snowflake URL is `https://xy12345.eu-west-1.snowflakecomputing.com`, use `xy12345.eu-west-1`.

---

### C3. Generate ADF config files

```bash
source venv/bin/activate
python scripts/setup_adf_config.py
```

This writes `adf-config/linkedService/LsSqlServer.json` and `LsSnowflake.json` using values from `.env`.

**How to verify it wrote correctly:**

1. **Script output** — You should see:
   ```
   Wrote adf-config/linkedService/LsSqlServer.json
   Wrote adf-config/linkedService/LsSnowflake.json
   ```

2. **Files exist** — In terminal:
   ```bash
   ls -la adf-config/linkedService/
   ```
   Both `LsSqlServer.json` and `LsSnowflake.json` should be listed.

3. **Check values (without exposing passwords)** — Open each file and confirm:
   - **LsSqlServer.json**: `server` = `localhost,1433` (or your SQL host), `database` = `LeadManagement`, `userName` = `sa`
   - **LsSnowflake.json**: `database` = `LEADMANAGEMENT`, `warehouse` = `LEAD_WH`
   - **Bad sign:** If you see placeholders like `"<your-password>"`, `"<org-account>"`, or `"<snowflake-username>"`, the corresponding values are missing from `.env`. Add them and run the script again.

4. **Quick check** — Run:
   ```bash
   cat adf-config/linkedService/LsSqlServer.json | head -15
   ```
   You should see valid JSON; `password` will show the actual value (keep this file private).

---

## Part D: GitHub Integration (Task Step 2 requirement)

The task requires **GitHub integration** for the ADF pipeline. Complete these steps so your pipeline definitions are version-controlled and the factory can load them from GitHub.

### D0a. Push project to GitHub (if not already)

1. Initialize Git and commit (only if this is a new project):
   ```bash
   cd <your-project-directory>
   git init
   git add .
   git commit -m "Initial commit: Step 1 SQL, Step 2 ADF, Step 3 Snowflake"
   ```
   **If the project already has Git:** run `git add .` and `git commit -m "..."` only if you have uncommitted changes.

2. Create a repository on [GitHub](https://github.com/new) (e.g. `vp-lead-pipeline`). Do **not** initialize it with a README if the local project already has commits.

3. Add remote and push:
   ```bash
   # If no remote exists yet:
   git remote add origin https://github.com/bhautik188/vp-lead-pipeline.git

   # If origin already exists, update the URL:
   # git remote set-url origin https://github.com/bhautik188/vp-lead-pipeline.git

   git branch -M main
   git push -u origin main
   ```

**Note:** Do **not** commit `adf-config/` or `.env` (they are gitignored). The `adf/` folder (templates only) is what ADF will load from Git.

---

### D0b. Configure GitHub in Azure Data Factory

After you create your Data Factory (E1), connect it to your GitHub repo:

1. In Data Factory Studio, go to **Manage** (left sidebar) → **Git configuration** (under Source control).
2. Click **Configure** (or **Set up code repository** from the home page).
3. Configure:
   - **Repository type:** GitHub
   - **GitHub repository owner:** Your GitHub username or organization
   - **Repository name:** Select your repo from the dropdown, or use **Use repository link** and paste `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`
   - **Collaboration branch:** `main`
   - **Publish branch:** `adf_publish` (default)
   - **Root folder:** `adf` (the folder that contains linkedService, dataset, pipeline, trigger)
   - **Import existing Data Factory resources to repository:** Uncheck (your repo already has the JSON files)
4. Click **Apply**. Authorize with GitHub when prompted (OAuth).
5. ADF will load pipelines, datasets, and triggers from the `adf/` folder in your repo.

**For private or organization repos:** GitHub may ask you to authorize the Azure Data Factory app. Follow the prompts to grant access.

---

## Part E: Create Azure Data Factory and Deploy (Task Step 2)

### E1. Create a Data Factory

1. Go to [portal.azure.com](https://portal.azure.com)  
2. **Create a resource** → search for **Data Factory**  
3. Create it (for example, resource group `lead-adf-rg`, factory name `lead-adf`)  
4. Open the factory → **Author & monitor**
5. Complete **Part D0b** above to connect GitHub (Manage → Git configuration → Configure).

---

### E2. Create or update linked services

If GitHub loaded linked services from `adf/`, they contain placeholders. Update them with real credentials:

1. Go to **Manage** → **Linked services**
2. Open **LsSqlServer** (or create if missing):
   - Use values from `adf-config/linkedService/LsSqlServer.json`
   - Server: `127.0.0.1,1433` (or your SQL host)
   - Database: `LeadManagement`, User: `sa`, Password: from `.env`
   - **Test connection** → Save
3. Open **LsSnowflake** (or create if missing):
   - Use values from `adf-config/linkedService/LsSnowflake.json`
   - Account identifier, database, warehouse, user, password
   - **Test connection** → Save
4. Open **LsAzureBlobStaging** (or create if missing) — required for SQL → Snowflake copy:
   - **New** → **Azure Blob Storage** → Name: `LsAzureBlobStaging`
   - Authentication: Account key
   - Select your storage account (create one in same resource group if needed) and container `adf-staging`
   - **Test connection** → Save

---

### E3. Set up Self-hosted Integration Runtime (required for local SQL Server)

**Why this is needed:** The default `AutoResolveIntegrationRuntime` runs inside Microsoft Azure’s network. When it tries to connect to `127.0.0.1`, it uses its own localhost (inside Azure), not your computer. Your SQL Server runs in Docker on your machine, so the cloud runtime cannot reach it.

A **Self-hosted Integration Runtime** runs on your local machine. When it connects to `127.0.0.1:1433`, it correctly refers to your local Docker SQL Server.

| | AutoResolveIntegrationRuntime | Self-hosted IR |
|---|-------------------------------|----------------|
| Runs where | Azure cloud | Your machine |
| Can reach `127.0.0.1`? | No (its own localhost) | Yes (your localhost) |
| For local SQL Server | Does not work | Required |

**Steps:**

1. **Manage** → **Integration runtimes**  
2. **New** → **Self-hosted**  
3. Name it (e.g. `SelfHostedIR`)  
4. Follow the wizard to **download and install** it on your machine (where SQL Server runs)  
5. After installation, edit **LsSqlServer** → set **Connect via integration runtime** to this Self-hosted IR (replace AutoResolveIntegrationRuntime)  
6. **Test connection** again

---

### E4. Verify datasets

After GitHub is connected (D0b), datasets should load from the repo. In **Manage** → **Datasets**, confirm:
- `DsSqlLeads`, `DsSqlWatermarkLookup`, `DsSnowflakeLeads`

If missing, **Import from file** using `adf/dataset/` JSON files.

---

### E5. Verify pipeline

In **Author** → **Pipelines**, confirm **PlLeadsSqlToSnowflake** is present (loaded from Git).

If missing, **Import** → select `adf/pipeline/PlLeadsSqlToSnowflake.json`.

---

### E6. Create and start trigger

1. **Manage** → **Triggers**  
2. **New** → **Schedule**  
3. Name: `TrgLeadsEvery30Min`  
4. Recurrence: every **30 minutes**  
5. Add pipeline: `PlLeadsSqlToSnowflake`  
6. **Publish** → **Start** the trigger

---

## Part F: Run the Pipeline

### Option 1: Azure Portal (manual run)

1. Open your Data Factory  
2. **Author & monitor** → ** pipelines**  
3. Open **PlLeadsSqlToSnowflake**  
4. **Add trigger** → **Trigger now** → **OK**

---

### Option 2: Azure CLI

```bash
az login
az datafactory pipeline create-run \
  --resource-group lead-adf-rg \
  --factory-name lead-adf \
  --name PlLeadsSqlToSnowflake
```

---

### Option 3: Scheduled runs

If the trigger is started, the pipeline runs automatically every 30 minutes.

---

## Part G: Verify the Result

1. In Snowflake, run:

```sql
USE DATABASE LEADMANAGEMENT;
SELECT COUNT(*) FROM LEADS;
```

You should see 100 rows after the first successful run.

---

## Summary: Order of Operations

| Order | Part | What you do |
|-------|------|-------------|
| 1 | A | Create SQL resources and load data |
| 2 | B | Create Snowflake warehouse, database, and Leads table |
| 3 | C | Configure credentials and generate ADF config |
| 4 | D0a | Push project to GitHub |
| 5 | E | Create Azure Data Factory |
| 6 | D0b | Configure GitHub in ADF (Manage → Git configuration) |
| 7 | E2–E6 | Create/update linked services, IR, verify datasets & pipeline, start trigger |
| 8 | F | Run the pipeline |
| 9 | G | Verify data in Snowflake |

---

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| Cannot connect to local SQL | **AutoResolveIntegrationRuntime cannot reach `127.0.0.1`** — it runs in Azure and treats localhost as its own. Use a **Self-hosted Integration Runtime** installed on your machine. Edit LsSqlServer → Connect via → select the Self-hosted IR. |
| Snowflake connection fails | Account identifier format, credentials, firewall |
| Pipeline fails on Copy | Snowflake LEADS table exists; column mapping is correct; LsAzureBlobStaging exists (required for SQL→Snowflake) |
| Watermark error | `load_leads_to_sql.py` ran and created `adt_watermark` and `sp_UpdateWatermark` |
