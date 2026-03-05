# Azure SQL Setup (Mac / No Docker)

Use Azure SQL Database instead of local Docker SQL. Works with **AutoResolveIntegrationRuntime** — no Self-hosted IR needed.

**Use your existing Data Factory** (lead-adf) — update the SQL linked service and datasets only. Pipeline, trigger, GitHub, and Snowflake stay as-is.

---

## 1. Create Azure SQL resources

### Via Azure Portal

1. Go to [portal.azure.com](https://portal.azure.com) and sign in.

2. Click **Create a resource** (top left), search for **SQL Database**, then click **Create**.

3. On the **Basics** tab:
   - **Subscription:** Your Azure subscription
   - **Resource group:** Use the same as your Data Factory (e.g. `lead-adf-rg`) or create a new one
   - **Database name:** `LeadManagement` (will be the database name in the connection string)
   - **Server:** Click **Create new**
     - **Server name:** e.g. `lead-sql` (must be globally unique; becomes `lead-sql.database.windows.net`)
     - **Location:** Same region as your Data Factory (e.g. `West Europe`)
     - **Authentication method:** Use SQL authentication
     - **Server admin login:** e.g. `sqladmin` (store this for `.env` as `SQL_USER`)
     - **Password:** Set a strong password (store this for `.env` as `SQL_PASSWORD`)
   - **Want to use SQL elastic pool:** No
   - **Compute + storage:** Click **Configure database**
     - **Free Trial:** Use **Basic** or **Standard S0** (both allowed; avoid "Free" tier — it often fails on Free Trial)
     - Basic = lowest cost; Standard S0 = slightly more but also allowed

4. Open the **Networking** tab:
   - **Connectivity method:** Public endpoint
   - **Firewall rules:** Enable **Allow Azure services and resources to access this server**
   - Add your IP: Click **Add current client IP address** (or add your IP range manually)
   - **Minimum TLS version:** 1.2 (default)

5. Click **Review + create**, then **Create**. Wait a few minutes for deployment.

6. After deployment, go to the database **Overview**. Note the **Server name** (e.g. `lead-sql.database.windows.net`) for `.env`.

**If deployment fails:** Click **Error details** on the failed resource. Free Trial allows Basic and Standard S0–S3 only. Redeploy with **Basic** tier (do not use "Free" or higher tiers).

### Via Azure CLI

```bash
az sql server create --name lead-sql --resource-group lead-adf-rg \
  --location westeurope --admin-user sqladmin --admin-password '<YourPassword>'

az sql db create --resource-group lead-adf-rg --server lead-sql \
  --name LeadManagement --service-objective Basic
```

**Note:** Add firewall rule so your IP can connect:
```bash
az sql server firewall-rule create --resource-group lead-adf-rg --server lead-sql \
  --name AllowMyIP --start-ip-address <YOUR_IP> --end-ip-address <YOUR_IP>
```

---

## 2. Update .env

```env
SQL_SERVER=lead-sql.database.windows.net
SQL_SERVER_PORT=1433
SQL_DATABASE=LeadManagement
SQL_USER=sqladmin
SQL_PASSWORD=<your-password>
```

Replace `lead-sql` with your server name, `sqladmin` with your admin username. Do **not** set `SELF_HOSTED_IR_NAME` — Azure SQL uses AutoResolve.

---

## 3. Load data

```bash
source venv/bin/activate
python load_leads_to_sql.py
```

Expected output: `Inserted 100 rows into Leads table (watermark table ready for Step 2 ADF)`

---

## 4. Generate ADF config

```bash
python scripts/setup_adf_config.py
```

This creates `LsSqlServer.json` as **AzureSqlDatabase** linked service (AutoResolve).

---

## 5. Update your existing ADF (lead-adf)

Open your Data Factory → **Author & monitor**.

### 5a. Replace LsSqlServer linked service

1. **Manage** → **Linked services**
2. Open **LsSqlServer** (the SQL Server one)
3. **Delete** it (pipelines will show errors until we fix this)
4. **New** → **Azure SQL Database**
5. **Name:** `LsSqlServer` (same name so pipeline keeps working)
6. **Connection string:** Paste the connection string from your local config:
   - First run `python scripts/setup_adf_config.py` (with `.env` set for Azure SQL) to generate `adf-config/`
   - Open `adf-config/linkedService/LsSqlServer.json`
   - Copy the value of `properties.typeProperties.connectionString`
   - It looks like: `Server=tcp:lead-sql.database.windows.net,1433;Initial Catalog=LeadManagement;User ID=sqladmin;Password=YourPassword;Encrypt=True;TrustServerCertificate=False;`
   - Paste this entire string into ADF’s **Connection string** field (do not edit in ADF if you have secrets — use Key Vault instead for production)
7. **Connect via:** AutoResolveIntegrationRuntime
8. **Test connection** → Save

### 5b. Replace SQL datasets

The pipeline needs **Azure SQL Database** datasets instead of SQL Server datasets. The old `SqlServerTable` type is not compatible with the new `AzureSqlDatabase` linked service.

1. **Manage** → **Datasets**
2. **Delete** `DsSqlLeads` and `DsSqlWatermarkLookup` (click the three dots → Delete). The pipeline will show validation errors until the new datasets exist — that’s expected.
3. **New** → **Azure SQL Database** — create **DsSqlLeads**:
   - **Name:** `DsSqlLeads`, **Linked service:** `LsSqlServer`
   - The UI only offers **Table** — do not use that (it loads the full table every run).
   - Click **Code** (</> icon) and paste this JSON, then **Save**:

     ```json
     {
       "name": "DsSqlLeads",
       "properties": {
         "linkedServiceName": { "referenceName": "LsSqlServer", "type": "LinkedServiceReference" },
         "parameters": { "WatermarkValue": { "type": "String" } },
         "type": "AzureSqlTable",
         "typeProperties": {
           "schema": "dbo",
           "table": "Leads",
           "sqlReaderQuery": "SELECT * FROM dbo.Leads WHERE UpdatedDateUtc > '@{dataset().WatermarkValue}'"
         }
       }
     }
     ```

4. **New** → **Azure SQL Database** — create **DsSqlWatermarkLookup** (name must match exactly — not `DsSqlWatermark`):
   - **Name:** `DsSqlWatermarkLookup`, **Linked service:** `LsSqlServer`
   - Click **Code** (</> icon) and paste this JSON, then **Save**:

     ```json
     {
       "name": "DsSqlWatermarkLookup",
       "properties": {
         "linkedServiceName": { "referenceName": "LsSqlServer", "type": "LinkedServiceReference" },
         "type": "AzureSqlTable",
         "typeProperties": {
           "schema": "dbo",
           "table": "adt_watermark",
           "sqlReaderQuery": "SELECT WatermarkValue FROM dbo.adt_watermark WHERE TableName = 'Leads'"
         }
       }
     }
     ```

**If publish fails** or Connection shows "Table: Select..." / "Loading..." — the Table UI does not work for this pipeline. Fix it via Code view:

1. Open **DsSqlLeads** → click **Code** (</> icon, top right) → **replace all** with the DsSqlLeads JSON above → **Save**.
2. Open **DsSqlWatermarkLookup** → click **Code** (</> icon) → **replace all** with the DsSqlWatermarkLookup JSON above → **Save**.
3. Publish again.

If errors persist, also verify the pipeline: **LookupWatermark** → Dataset: `DsSqlWatermarkLookup`; **CopyLeads** → Source: `DsSqlLeads` (parameter `WatermarkValue`); **UpdateWatermark** → Linked service: `LsSqlServer`.

### 5c. Azure Blob staging (required for Step 2 SQL → Snowflake copy)

ADF only allows direct Snowflake copy from Blob/S3. Staging is required. **Works on Mac + Azure trial.**

#### 5c.1 Create storage account (Azure trial, ~$0.02/month for small loads)

1. Go to [portal.azure.com](https://portal.azure.com) in your browser (Safari, Chrome, etc.).
2. **Create a resource** → search **Storage account** → **Create**.
3. **Basics:**
   - **Resource group:** same as ADF (e.g. `lead-adf-rg`)
   - **Storage account name:** e.g. `leadadfstaging` (globally unique; lowercase, no spaces)
   - **Region:** same as ADF
   - **Performance:** Standard
   - **Redundancy:** LRS (cheapest)
4. **Review** → **Create**. Wait ~30 seconds.
5. Open the new storage account → **Containers** → **+ Container**:
   - **Name:** `adf-staging`
   - **Public access:** Private
6. **Save** the container.

#### 5c.2 Generate SAS URI (required for Snowflake staging)

Snowflake staged copy only works with **SAS URI** auth — not account key.

1. **Azure Portal** → open storage account `leadadfstaging`
2. Left menu → **Shared access signature**
3. **Allowed resource types:** Blob and Container
4. **Allowed permissions:** Read, Write, Delete, List (all needed for staging)
5. **Expiry:** e.g. 1 year from now (or longer for trials)
6. **Generate SAS and connection string**
7. Copy the **Blob SAS URL** — it looks like:  
   `https://leadadfstaging.blob.core.windows.net/?sv=...&se=...&sig=...`

#### 5c.3 Create linked service in ADF (SAS URI)

1. **ADF** → **Manage** → **Linked services** → open **LsAzureBlobStaging** (or **+ New** → **Azure Blob Storage**)
2. **Name:** `LsAzureBlobStaging`
3. **Authentication method:** **SAS URI**
4. **SAS URI:** Paste the Blob SAS URL from 5c.2
5. **Test connection** → **Create** or **Save**

#### 5c.4 Sync and publish

- Pipeline in repo already uses `enableStaging: true` and path `adf-staging`.
- If changes were made in Git, sync: **Author** → switch branch or refresh.
- **Publish all**.

**If you get "Staged copying data to Snowflake is supported when uses Azure Blob storage with SAS URI authentication"** — the staging linked service must use **SAS URI**, not Account key. Follow 5c.2–5c.3 to switch.

### 5d. No changes needed

- **LsSnowflake**, **DsSnowflakeLeads** — keep as-is
- **PlLeadsSqlToSnowflake** — uses staging (in repo)
- **TrgLeadsEvery30Min** — no changes
- **GitHub** — no changes

5. **Publish all**

**If "Lookup activity Source type is required"**: Open **LookupWatermark** → **Settings** → ensure **Source dataset** = `DsSqlWatermarkLookup`. If set, try Validate again or close/reopen the pipeline.


---

## Summary

| Step    | Local Docker        | Azure SQL                         |
|---------|---------------------|-----------------------------------|
| SQL     | Docker container    | Azure SQL Database                |
| IR      | Self-hosted required| AutoResolve                       |
| load script | Same             | Same (different .env)             |
| ADF linked service | SqlServer   | AzureSqlDatabase + LsAzureBlobStaging (staging) |
| ADF datasets | SqlServerTable  | AzureSqlTable                    |
