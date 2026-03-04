# ADF GitHub Integration – Setup Guide

This guide configures Azure Data Factory with GitHub for Step 2 of the Data Engineering Task.

---

## Expected Folder Structure

Your repository must have this layout. **Root folder** in ADF Git config = `adf`:

```
your-repo/
├── adf/
│   ├── linkedServices/
│   │   ├── Ls_SqlServer.json
│   │   └── Ls_Snowflake.json
│   ├── datasets/
│   │   ├── Ds_Leads_Sql.json
│   │   └── Ds_Leads_Snowflake.json
│   ├── pipelines/
│   │   └── Pl_SqlToSnowflake.json
│   ├── triggers/
│   │   └── Tr_Every30Min.json
│   ├── factory/
│   │   └── adf-lead-pipeline.json
│   └── publish_config.json
├── sql/
├── logicapp/
└── ...
```

The Data Factory name in `factory/adf-lead-pipeline.json` must match the ADF resource name in Azure.

---

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. **Repository name:** e.g. `lead-pipeline` or `vp-lead-project`
3. **Public** or **Private**
4. Do **not** initialize with README if you already have local files
5. Click **Create repository**

---

## Step 2: Push Project to GitHub

From your project folder:

```bash
git init
git add .
git commit -m "Initial commit - ADF pipeline, SQL, Logic App"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Use **SSH** if you prefer:

```bash
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
```

Ensure the `adf/` folder and all JSON files are committed.

---

## Step 3: Create Azure Data Factory

1. Azure Portal → **Data factories** → **Create**
2. **Name:** `adf-lead-pipeline` (must match `factory/adf-lead-pipeline.json`)
3. **Resource group:** e.g. `rg-lead-management`
4. **Region:** e.g. West Europe
5. **Git configuration:** **Configure git later**
6. Click **Create**

---

## Step 4: Connect ADF to GitHub

1. Open your Data Factory → **Launch studio**
2. **Manage** (gear icon) → **Source control** → **Git configuration**
3. Click **Configure** (or **Set up code repository** from Home)
4. **Repository type:** **GitHub**
5. **Authorize** → sign in to GitHub and grant access
6. **GitHub account:** Select your account
7. **Repository name:** Select your repository
8. **Collaboration branch:** `main`
9. **Publish branch:** `adf_publish`
10. **Root folder:** `adf` (exact value, no leading slash)
11. **Import existing resources to repository:** **Unchecked**
12. Click **Apply**

---

## Step 5: Import Resources

1. On the **Git configuration** page, click **Import resources**
2. Wait for the import to complete
3. Go to **Author** and confirm Pipelines, Datasets, Linked services, Triggers are loaded

If Import fails, use **Manual add** (Step 6).

---

## Step 6: Manual Add (If Import Fails)

Add each resource in order:

| Order | Type | Name | Action |
|-------|------|------|--------|
| 1 | Linked service | Ls_SqlServer | Manage → Linked services → + New → SQL Server → **Code** → paste `adf/linkedServices/Ls_SqlServer.json` |
| 2 | Linked service | Ls_Snowflake | Manage → Linked services → + New → Snowflake → **Code** → paste `adf/linkedServices/Ls_Snowflake.json` |
| 3 | Dataset | Ds_Leads_Sql | Author → Datasets → + → SQL Server table → **Code** → paste `adf/datasets/Ds_Leads_Sql.json` |
| 4 | Dataset | Ds_Leads_Snowflake | Author → Datasets → + → Snowflake table → **Code** → paste `adf/datasets/Ds_Leads_Snowflake.json` |
| 5 | Pipeline | Pl_SqlToSnowflake | Author → Pipelines → + → **Code** → paste `adf/pipelines/Pl_SqlToSnowflake.json` |
| 6 | Trigger | Tr_Every30Min | Manage → Triggers → + New → Schedule → **Code** → paste `adf/triggers/Tr_Every30Min.json` → link to Pl_SqlToSnowflake |

---

## Step 7: Configure and Publish

1. Open each **linked service** and set real values: server, database, user, password
2. In the pipeline, set parameter **LogicAppAlertUrl** if using email alerts (see `logicapp/README.md`)
3. Click **Save all**
4. Click **Publish**

After publishing, changes will be committed to your GitHub repo.

---

## Important Settings

| Setting | Value |
|---------|-------|
| Root folder | `adf` |
| Collaboration branch | `main` |
| Publish branch | `adf_publish` |
| Factory name | Must match `factory/adf-lead-pipeline.json` (e.g. `adf-lead-pipeline`) |

---

## Troubleshooting

| Issue | Action |
|-------|--------|
| Import shows 0 resources | Confirm root folder is `adf`. Confirm JSON files exist in `adf/linkedServices`, `adf/datasets`, etc. Use Manual add (Step 6). |
| Factory name mismatch | Rename your ADF in Azure to match `adf-lead-pipeline`, or update `factory/adf-lead-pipeline.json` to match your ADF name. |
| Repository not found | Ensure the repo exists and you have push access. Check URL and credentials. |
| Duplicate factory folders | Keep only `adf/factory/`. Do not have `/factory/` at the repo root. |
