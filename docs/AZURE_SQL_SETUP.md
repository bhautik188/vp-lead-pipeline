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

The pipeline needs **Azure SQL Database** datasets instead of SQL Server datasets:

1. **Manage** → **Datasets**
2. **Delete** `DsSqlLeads` and `DsSqlWatermarkLookup`
3. **New** → **Azure SQL Database**:
   - Name: `DsSqlLeads`
   - Linked service: `LsSqlServer`
   - Table: `dbo.Leads`
   - Add parameter: `WatermarkValue` (String)
   - **Connection** → Edit → Query: `SELECT * FROM dbo.Leads WHERE UpdatedDateUtc > '@{dataset().WatermarkValue}'`
4. **New** → **Azure SQL Database**:
   - Name: `DsSqlWatermarkLookup`
   - Linked service: `LsSqlServer`
   - **Connection** → Edit → Query: `SELECT WatermarkValue FROM dbo.adt_watermark WHERE TableName = 'Leads'`

### 5c. No changes needed

- **LsSnowflake**, **DsSnowflakeLeads** — keep as-is
- **PlLeadsSqlToSnowflake** — no changes
- **TrgLeadsEvery30Min** — no changes
- **GitHub** — no changes

5. **Publish all**

---

## Summary

| Step    | Local Docker        | Azure SQL                         |
|---------|---------------------|-----------------------------------|
| SQL     | Docker container    | Azure SQL Database                |
| IR      | Self-hosted required| AutoResolve                       |
| load script | Same             | Same (different .env)             |
| ADF linked service | SqlServer   | AzureSqlDatabase                  |
| ADF datasets | SqlServerTable  | AzureSqlTable                    |
