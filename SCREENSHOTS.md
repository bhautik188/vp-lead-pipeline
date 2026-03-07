# Screenshots — Data Engineering Task

Visual proof of pipeline implementation.

---

## Step 2 — Azure Data Factory

**Pipeline design** — Lookup watermark → Copy Leads → Update watermark (incremental load)

![ADF Pipeline Design](screenshots/adf-pipeline-design.png)

**Pipeline run** — Successful execution

![ADF Pipeline Success](screenshots/adf-pipeline-success-or-failure.png)

**Trigger** — Schedule every 30 minutes (task requirement)

![ADF Trigger](screenshots/adf-trigger-30min.png)

**GitHub integration** — Repo connected (task requirement)

![ADF GitHub](screenshots/adf-github-integration.png)

---

## Step 3 — Snowflake

**LEADS table** — Data synced from SQL via ADF

![Snowflake Leads](screenshots/snowflake-leads.png)

---

## Step 4 — Python Transformation

**LeadEvents table** — Transformed from Leads (event types per state)

![Snowflake LeadEvents](screenshots/snowflake-leadevents.png)
