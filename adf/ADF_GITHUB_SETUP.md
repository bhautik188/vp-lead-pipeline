# Azure Data Factory - GitHub Integration (Detailed Guide)

This guide walks you through connecting Azure Data Factory to GitHub for source control, collaboration, and optional CI/CD.

---

## Prerequisites Before You Start

| Requirement | Details |
|-------------|---------|
| **Azure subscription** | Active subscription with permission to create resources |
| **GitHub account** | Personal or organization account |
| **GitHub repository** | Repository created (can be empty or have your project code) |
| **Data Factory created** | An Azure Data Factory resource already exists in Azure |
| **ADF JSON files** | Your project has the `adf/` folder with linkedServices, datasets, pipelines, triggers |

---

## Part 1: Create Azure Data Factory (If Not Already Created)

### Step 1.1: Open Azure Portal

1. Go to [https://portal.azure.com](https://portal.azure.com) and sign in.
2. In the top search bar, type **Data factories** and press Enter.
3. Click **Data factories** under Services.

### Step 1.2: Create Data Factory

1. Click **+ Create** (top left).
2. On the **Basics** tab:
   - **Subscription**: Select your subscription.
   - **Resource group**: Create new (e.g. `rg-lead-management`) or select existing.
   - **Region**: Choose a region (e.g. East US, West Europe).
   - **Name**: Enter a unique name (e.g. `adf-lead-pipeline`). Must be globally unique.
   - **Git configuration**: Leave **Configure git later** selected for now.
3. Click **Review** at the bottom, then **Create**.
4. Wait for deployment. Click **Go to resource** when done.

---

## Part 2: Push Your Project to GitHub (If Not Already Done)

### Step 2.1: Create a GitHub Repository

1. Go to [https://github.com](https://github.com).
2. Click the **+** icon (top right) → **New repository**.
3. **Repository name**: e.g. `vp-lead-project` or `lead-data-pipeline`.
4. **Description** (optional): "Lead management data pipeline - ADF, SQL, Snowflake".
5. **Public** or **Private**: Choose as needed.
6. **Do not** initialize with README, .gitignore, or license if you already have local files.
7. Click **Create repository**.

### Step 2.2: Set Up SSH Key and Push Your Local Project to GitHub

#### Step 2.2a: Generate an SSH Key (if you don't have one)

1. Open a terminal (Terminal on macOS/Linux, PowerShell or Git Bash on Windows).
2. Run:
   ```bash
   ssh-keygen -t ed25519 -C "bhautik188@github.com"
   ```
   - Replace `your-email@example.com` with your GitHub email.
   - When asked **"Enter file in which to save the key"**, press Enter to use the default (`~/.ssh/id_ed25519`).
   - When asked for a passphrase, either enter one (recommended) or press Enter for none.
3. The key is saved as `~/.ssh/id_ed25519` (private) and `~/.ssh/id_ed25519.pub` (public).

**Alternative (RSA):** If your system doesn't support Ed25519:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
   ```

#### Step 2.2b: Add the SSH Key to GitHub

1. Copy your **public key** to the clipboard:
   - **macOS:** `pbcopy < ~/.ssh/id_ed25519.pub`
   - **Linux:** `xclip -sel clip < ~/.ssh/id_ed25519.pub` or `cat ~/.ssh/id_ed25519.pub` and copy manually
   - **Windows (Git Bash):** `cat ~/.ssh/id_ed25519.pub` and copy the output
2. Go to [GitHub](https://github.com) → **Settings** (your profile) → **SSH and GPG keys**.
3. Click **New SSH key**.
4. **Title**: e.g. `My Laptop` or `Work PC`.
5. **Key type**: **Authentication Key**.
6. **Key**: Paste the public key (starts with `ssh-ed25519` or `ssh-rsa`).
7. Click **Add SSH key**.

#### Step 2.2c: Add Remote and Push Using SSH

From your project folder (e.g. `VP Project/`):

```bash
# Initialize git if not already done
git init

# Add remote using SSH URL (replace with your username and repo name)
git remote add origin git@github.com:bhautik188/vp-lead-project.git

# Add all files
git add .

# Commit
git commit -m "Initial commit - ADF, SQL, Logic App"

# Push (main branch)
git branch -M main
git push -u origin main
```

**SSH URL format:** `git@github.com:USERNAME/REPO_NAME.git`

**If you already have an HTTPS remote**, switch to SSH:
```bash
git remote set-url origin git@github.com:bhautik188/vp-lead-project.git
git push -u origin main
```

**Verify SSH connection:**
```bash
ssh -T git@github.com
```
You should see: `Hi USERNAME! You've successfully authenticated...`

**Ensure your `adf/` folder structure is present:**

```
adf/
├── linkedServices/
│   ├── Ls_SqlServer.json
│   └── Ls_Snowflake.json
├── datasets/
│   ├── Ds_Leads_Sql.json
│   └── Ds_Leads_Snowflake.json
├── pipelines/
│   └── Pl_SqlToSnowflake.json
└── triggers/
    └── Tr_Every30Min.json
```

---

## Part 3: Connect ADF to GitHub - Detailed Steps

### Step 3.1: Open Git Configuration in ADF

**Important:** Git configuration is **inside Azure Data Factory Studio** (the authoring UI), not on the Azure Portal resource page. You must open the Data Factory Studio first.

#### Method A: From Azure Portal (recommended first-time path)

1. Go to [https://portal.azure.com](https://portal.azure.com) and sign in.
2. In the top search bar, type your **Data Factory name** (e.g. `adf-lead-pipeline`) and press Enter.
3. Under **Resources**, click your Data Factory to open its **Overview** page.
4. On the Overview page, find the **Open Azure Data Factory Studio** button (or **Author & Monitor** in older UI).
5. Click **Open Azure Data Factory Studio**.
   - A new tab opens with the ADF authoring interface (blue/purple theme, left sidebar with icons).
6. You are now in **Azure Data Factory Studio**. Use one of the following to reach Git configuration:

   **Option 1 – Management hub (most reliable)**  
   - In the **left sidebar**, click the **gear icon** (Manage / Management hub).  
   - The left menu expands. Under **Source control**, click **Git configuration**.  
   - If no repository is connected, you'll see **Configure** – click it.

   **Option 2 – Home page**  
   - Click the **Azure Data Factory** logo or **Home** (house icon) in the top-left to go to the home page.  
   - At the top of the home page, look for **Set up code repository** and click it.

   **Option 3 – Authoring canvas**  
   - If you're on any pipeline/canvas view, click the **Data Factory name** (or drop-down) in the top-left.  
   - In the drop-down menu, select **Set up code repository**.

#### Method B: Direct link to ADF Studio

1. Go to `https://adf.azure.com` (or the URL shown when you open your Data Factory).
2. Select your **subscription**, **resource group**, and **Data Factory** if prompted.
3. Follow **Option 1** above: left sidebar → **gear icon (Manage)** → **Source control** → **Git configuration**.

#### What you should see

- A configuration pane titled **Configure code repository** or **Git configuration**.
- Fields for **Repository type**, **GitHub account**, **Repository name**, **Branch**, **Root folder**, etc.
- If Git is already configured, you'll see **Edit** instead of **Configure**.

#### If you still can't find it

| Where you are | What to do |
|---------------|------------|
| **Azure Portal** – Data Factory resource page (Overview, Metrics, etc.) | Git settings are **not** here. Click **Open Azure Data Factory Studio** and then follow Method A. |
| **ADF Studio** – Left sidebar shows Pipelines, Datasets, etc. | Look for the **gear icon** at the bottom of the left sidebar (Manage). Click it, then **Git configuration** under Source control. |
| **ADF Studio** – No gear icon visible | Try the **three-line menu (☰)** if the sidebar is collapsed. Click it to expand, then find the gear icon. |

### Step 3.2: Authorize GitHub

1. You'll see a blade titled **Configure Git repository** or **Git configuration**.
2. **Repository type**: Select **GitHub** from the dropdown.
   - (Other options: Azure DevOps, Git with public access.)
3. Under **GitHub**, you'll see **Authorize Azure Data Factory to access your GitHub** or similar.
4. Click **Authorize Azure Data Factory** (or **Authorize**).
5. A new tab or popup will open asking you to sign in to GitHub (if not already).
6. Sign in with your GitHub username and password (or passkey).
7. GitHub may ask: **Authorize AzureDataFactory?** – Click **Authorize AzureDataFactory**.
8. You may be redirected back to Azure or see "Authorization successful". Close the tab if it doesn't close automatically.
9. Return to the Azure Portal tab with the ADF Git configuration.

### Step 3.3: Select GitHub Account and Organization

1. After authorization, the **GitHub account** dropdown will be populated.
2. **GitHub account**: Select your account (e.g. `your-username`).
3. **Organization**: If you use a GitHub Organization:
   - Select the organization from the dropdown.
   - If using a personal repo, leave this as your username or select **-- No organization --** / your personal account.
4. **Repository name**: Select your repository from the dropdown (e.g. `vp-lead-project`).
   - If the repo doesn't appear, click the refresh icon and ensure you've authorized and pushed to GitHub.

### Step 3.4: Select Branch and Root Folder

1. **Collaboration branch** (or **Branch**):
   - Select **main** if that's your default branch.
   - Or select the branch where your `adf/` folder lives (e.g. `main`, `master`, `develop`).
2. **Root folder**:
   - If your repo root contains the `adf/` folder directly: Enter `/` or leave blank.
   - If your ADF files are in a subfolder (e.g. project has `VP Project/adf/`): Enter `adf` or the path to the folder that contains `linkedServices`, `datasets`, etc.
   - **Important**: The root folder is the parent of `linkedServices`, `datasets`, `pipelines`, `triggers`. So if structure is `repo/adf/linkedServices/`, use `adf` as root.
3. **Import existing Data Factory resources to repository**:
   - Check this box **if** you have made changes in ADF (in the portal) that are **not** yet in Git – ADF will export them and commit to your branch.
   - **Uncheck** if your repo already has the complete `adf/` folder and you want ADF to **load from Git** (import from repo) instead.
4. **Publish branch** (if shown):
   - Typically `adf_publish` – used when you click Publish. Leave as default.

### Step 3.5: Apply Git Configuration

1. Click **Apply** (or **Save**) at the bottom.
2. A confirmation message may appear. Click **OK** or **Yes**.
3. Wait a few seconds. ADF will:
   - Connect to your GitHub repo
   - Either import from repo (if unchecked) or export to repo (if checked)
   - Create or switch to the selected branch
4. You may see **"Git configuration has been applied successfully"** or similar.

### Step 3.6: Open Data Factory Studio

**When to do this:** If you configured Git from within ADF Studio (via Manage → Git configuration), you're already there – skip to Part 4. Do this step only if you configured Git from the Azure Portal resource page or a different entry point.

**Where exactly to find "Open Azure Data Factory Studio":**

1. Go to [Azure Portal](https://portal.azure.com).
2. In the top search bar, type your **Data Factory name** and open the resource.
3. You'll see the Data Factory resource page with tabs: **Overview**, **Activity log**, **Access control**, etc.
4. Stay on (or click) the **Overview** tab.
5. Look at the **top-center** or **top-right** of the main content area – you’ll see a horizontal toolbar with buttons.
6. The button is usually labeled:
   - **Open Azure Data Factory Studio**, or  
   - **Open** (with a link icon), or  
   - **Author & Monitor** (in older portal versions)
7. It’s in the same toolbar area as **Refresh**, **Delete**, **Move**, etc.
8. Click it. A new browser tab opens with the ADF authoring UI (`adf.azure.com` or similar).

**If you don’t see it:**
- Scroll up on the Overview page – the button is often near the factory name.
- Some layouts show it as a **card** or **tile** under “Quick actions” or “Get started”.
- You can also go directly to **https://adf.azure.com**, pick your subscription and Data Factory, and open it from there.

**Once in ADF Studio, in the left pane you should see:**
- **Pipelines**
- **Datasets**
- **Linked services**
- **Triggers**
- A Git branch indicator (e.g. `main`) near the bottom of the sidebar or in the top bar.

---

## Part 4: Verify and Load Resources from Git

### Step 4.1: Check Branch

1. In ADF Studio, look for the **branch name** in the top bar or left sidebar (e.g. `main`).
2. Click it to see branch selector. Ensure you're on the branch that has your `adf/` content.

### Step 4.2: Import/Load from Repository

1. If your pipelines, datasets, and linked services **do not appear**:
   - Go to **Manage** (gear icon) → **Git configuration**.
   - Ensure **Root folder** matches where your `adf/` JSON files live.
   - If you had "Import existing resources" checked, ADF may have overwritten. Switch to your branch and re-sync.
2. If resources **still don't show**: Ensure the JSON files are in the correct structure and pushed to GitHub. Refresh the repo connection.
3. Click **Sync** or **Pull** (if visible) to fetch latest from Git.

### Step 4.3: Confirm Structure

You should see:

| Folder | Contents |
|-------|----------|
| **Linked services** | Ls_SqlServer, Ls_Snowflake |
| **Datasets** | Ds_Leads_Sql, Ds_Leads_Snowflake |
| **Pipelines** | Pl_SqlToSnowflake |
| **Triggers** | Tr_Every30Min |

---

## Part 5: Edit → Save → Publish Workflow

### Step 5.1: Making Changes (Edit)

1. Open a pipeline (e.g. **Pl_SqlToSnowflake**) by clicking it.
2. Make your edits (e.g. set parameter **LogicAppAlertUrl**).
3. Configure linked services with real connection details (SQL Server, Snowflake) – these are not in Git for security.

### Step 5.2: Save to Git

1. After editing, click **Save** (top bar, or Ctrl+S).
2. A **Commit to repository** dialog appears:
   - **Commit message**: Enter a description (e.g. "Add Logic App URL for failure alerts").
   - **Commit directly to main** (or your branch) – or select **Create new branch** to commit to a feature branch.
3. Click **OK** or **Commit**.
4. Your changes are committed to your GitHub branch. You can verify on GitHub.com.

### Step 5.3: Publish

1. Click **Publish** (or **Publish all**) in the top bar.
2. A **Publish** dialog shows what will be published (new/changed resources).
3. Click **OK** to confirm.
4. ADF generates ARM templates and pushes to the **adf_publish** branch.
5. You can verify on GitHub: switch to `adf_publish` branch and see `ARMTemplateForFactory.json`, `ARMTemplateParametersForFactory.json`.

---

## Part 6: Root Folder Examples

| Repo structure | Root folder value |
|----------------|-------------------|
| `repo/linkedServices/`, `repo/pipelines/`, etc. at root | `/` or empty |
| `repo/adf/linkedServices/`, `repo/adf/pipelines/` | `adf` |
| `repo/VP Project/adf/linkedServices/` | `VP Project/adf` or `adf` (depending on exact layout) |

**Rule:** Root folder = path to the folder that **contains** `linkedServices`, `datasets`, `pipelines`, `triggers`.

---

## Part 7: Optional - CI/CD with GitHub Actions

### Step 7.1: Create Azure Service Principal

1. In Azure Portal, go to **Microsoft Entra ID** (Azure Active Directory) → **App registrations**.
2. Click **+ New registration**.
3. **Name**: e.g. `sp-adf-deploy`.
4. **Supported account types**: Choose **Accounts in this organizational directory only**.
5. Click **Register**.
6. Note the **Application (client) ID** and **Directory (tenant) ID**.
7. Go to **Certificates & secrets** → **+ New client secret** → Add description, expiration → **Add**.
8. Copy the **Value** (secret) – you won't see it again.
9. Go to **Subscriptions** → your subscription → **Access control (IAM)** → **Add role assignment**.
10. Role: **Contributor** (or **Owner** for the resource group). Assign to the app registration. Save.

### Step 7.2: Create JSON for AZURE_CREDENTIALS

Create this JSON (replace placeholders):

```json
{
  "clientId": "<Application (client) ID>",
  "clientSecret": "<Client secret value>",
  "subscriptionId": "<Your Azure subscription ID>",
  "tenantId": "<Directory (tenant) ID>"
}
```

### Step 7.3: Add GitHub Secrets

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**.
2. Click **New repository secret**.
3. **Name**: `AZURE_CREDENTIALS`, **Value**: paste the entire JSON (one line is fine).
4. Add another secret: **Name** `ADF_RESOURCE_GROUP`, **Value**: your resource group name (e.g. `rg-lead-management`).
5. Save.

### Step 7.4: Use the Workflow

The project includes `.github/workflows/adf-deploy.yml`. When you push to `adf_publish`, it will run. Remove `continue-on-error: true` from the workflow once secrets are configured.

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| **"Authorize" doesn't open or fails** | Disable popup blockers. Try in incognito. Ensure you're signed into GitHub. |
| **Repository not in dropdown** | Ensure the repo exists and you've pushed at least one commit. Refresh the dropdown. Check GitHub account/org selection. |
| **"Root folder not found" or empty resources** | Verify path: Root folder must be the parent of `linkedServices`, etc. Check for typos and case sensitivity. |
| **Publish creates empty adf_publish** | Ensure you've clicked **Publish** (not just Save). Publish generates ARM from published resources. |
| **Linked service shows "Invalid" after load** | Connection details (passwords, etc.) are not in Git. Re-enter them in ADF Studio for each linked service. |
| **Branch not showing / wrong branch** | Use branch selector in ADF Studio. Pull/sync to refresh. |
| **"Import existing resources" overwrote my files** | If repo had correct files, uncheck that option. Restore from Git history if needed, then re-apply Git config with import unchecked. |

---

## Summary: Checklist

- [ ] Azure Data Factory created
- [ ] GitHub repo created and project pushed
- [ ] ADF Git configuration: GitHub selected, authorized
- [ ] Repository and branch selected
- [ ] Root folder set correctly
- [ ] Resources (pipelines, datasets, linked services) visible in ADF Studio
- [ ] Linked services updated with real connection details
- [ ] Changes saved to Git (commit)
- [ ] Published to `adf_publish` branch
- [ ] (Optional) GitHub Actions secrets configured for CI/CD
