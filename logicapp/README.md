# ADF Failure Email Alert - Logic App Setup (Detailed Guide)

This Logic App receives pipeline failure details from Azure Data Factory and sends an email alert. Follow this guide step-by-step in the Azure Portal.

---

## Part 1: Create the Logic App

### Step 1.1: Open Azure Portal and Create Resource

1. Go to [https://portal.azure.com](https://portal.azure.com) and sign in.
2. In the top search bar, type **Logic App** and press Enter.
3. Click **Logic App** in the results (under "Marketplace" or "Services").
4. Click the **+ Create** button (top left of the Logic App blade).

### Step 1.2: Fill in Basics

On the **Create Logic App** page, you'll see tabs: **Basics**, **Hosting**, **Tags**, **Review + create**.

**Basics tab:**

| Field | What to select or enter |
|-------|--------------------------|
| **Subscription** | Your Azure subscription (e.g. "Pay-As-You-Go", "Visual Studio Enterprise") |
| **Resource group** | Click **Create new** and enter `rg-adf-alerts`, or select an existing resource group. |
| **Logic App name** | `LogicApp-ADF-FailureAlert` (or any name you prefer) |
| **Region** | Choose a region close to your Data Factory (e.g. East US, West Europe) |
| **Plan type** | Select **Consumption** (serverless, pay-per-execution). Do **not** select Standard unless you have specific requirements. |

### Step 1.3: Hosting Tab

| Field | What to select |
|-------|----------------|
| **Storage account** | Leave **Create new** selected. Azure will create a storage account for the Logic App's run history. |
| **Location** | Same as your Logic App region (auto-filled). |

### Step 1.4: Create the Logic App

1. Click **Review + create** at the bottom.
2. Wait for validation to pass (green checkmark).
3. Click **Create**.
4. Wait for deployment to complete (usually 30–60 seconds). Click **Go to resource** when it appears.

---

## Part 2: Configure the HTTP Trigger

### Step 2.1: Open the Designer

1. You should now be on the Logic App resource page.
2. In the left menu under **Development tools**, click **Logic app designer**.
3. Under **Templates**, you'll see options like "Blank Logic App", "When a HTTP request is received", etc.
4. Click **Blank Logic App** (or scroll to the bottom and select the blank workflow).

### Step 2.2: Add the HTTP Request Trigger

1. In the designer, you'll see a search box: **Search connectors and triggers**.
2. Type **When a HTTP request is received**.
3. In the results, under **Triggers**, click **When a HTTP request is received** (it has an icon of a lightning bolt or request arrow).
4. A new tile will appear with the trigger.

### Step 2.3: Configure the Request Schema

1. Click **Use sample payload to generate schema** in the HTTP trigger tile (you may need to expand the tile or scroll down).
2. A text box will open. Delete any existing text and paste exactly:

```json
{
    "pipelineName": "Pl_SqlToSnowflake",
    "runId": "abc-123",
    "status": "Failed",
    "failedActivity": "Copy_Leads_SqlToSnowflake",
    "errorMessage": "Connection timeout"
}
```

3. Click **Done**.
4. The schema will be generated. You should see fields like `pipelineName`, `runId`, `status`, `failedActivity`, `errorMessage` in the schema section.

### Step 2.4: Save to Generate the HTTP POST URL

1. Click **Save** in the top toolbar (or press Ctrl+S).
2. After saving, the HTTP trigger tile will show **HTTP POST URL**.
3. Click **Copy** next to the HTTP POST URL and save it somewhere safe (Notepad, etc.). You will need this URL for the ADF pipeline.

---

## Part 3: Add the Send Email Action

### Step 3.1: Add a New Step

1. Under the HTTP trigger tile, click **+ New step**.
2. In the **Choose an action** pane that opens, you'll see a search box.

### Step 3.2: Choose Email Connector

**Option A: Office 365 Outlook (work or school email)**

1. In the search box, type **Office 365 Outlook**.
2. In the results, under **Actions**, find **Send an email (V2)**.
   - If you only see **Send an email** (without V2), use that instead.
3. Click **Send an email (V2)**.
4. If prompted **Sign in to Office 365 Outlook**, click it.
5. A popup will open. Sign in with your work/school Microsoft account (e.g. `you@company.com`).
6. Grant permissions if asked (**Yes** or **Accept**).
7. After sign-in, the action tile will expand with fields.

**Option B: Gmail (personal email)**

1. In the search box, type **Gmail**.
2. Click **Send an email (V2)** under Gmail actions.
3. Click **Sign in to Gmail** when prompted.
4. Sign in with your Google account and grant access.
5. The action tile will expand.

### Step 3.3: Configure the Email Fields

Once the Send email action is added:

**For Office 365 Outlook – Send an email (V2):**

| Field | What to enter | How |
|-------|---------------|------|
| **To** | Your email address | Type it directly (e.g. `you@company.com`) or click the field and select from contacts. |
| **Subject** | Dynamic subject with pipeline name | Click inside **Subject**. In the **Expression** tab (or the dynamic content panel), enter: `ADF Pipeline Failed: ` then click **Add dynamic content** and select **pipelineName** from the trigger output. Or type: `ADF Pipeline Failed: @{triggerBody()?['pipelineName']}` |
| **Body** | Failure details | See below. |

**For Gmail – Send an email (V2):**

| Field | What to enter |
|-------|---------------|
| **To** | Your email address |
| **Subject** | Same as above |
| **Body** | Same as below |

**Email Body (for both):**

1. Click inside the **Body** field.
2. You can either:
   - **Option 1 – Dynamic content:** Click **Add dynamic content**. For each line, insert the matching field from **When a HTTP request is received** (pipelineName, runId, status, failedActivity, errorMessage).
   - **Option 2 – Expression:** Switch to **Expression** (if available) or type directly:

```
Pipeline: @{triggerBody()?['pipelineName']}
Run ID: @{triggerBody()?['runId']}
Status: @{triggerBody()?['status']}
Failed Activity: @{triggerBody()?['failedActivity']}
Error: @{triggerBody()?['errorMessage']}

Check the ADF pipeline run for more details.
```

3. For richer formatting, use HTML in the Body (if your connector supports it):

```html
<p><strong>Azure Data Factory Pipeline Failure</strong></p>
<p><strong>Pipeline:</strong> @{triggerBody()?['pipelineName']}</p>
<p><strong>Run ID:</strong> @{triggerBody()?['runId']}</p>
<p><strong>Failed Activity:</strong> @{triggerBody()?['failedActivity']}</p>
<p><strong>Error:</strong> @{triggerBody()?['errorMessage']}</p>
<p>Check the ADF pipeline run in Azure Portal for more details.</p>
```

### Step 3.4: Save the Logic App

1. Click **Save** in the top toolbar.
2. Your Logic App should now show two tiles: **When a HTTP request is received** → **Send an email (V2)**.

---

## Part 4: Get the HTTP POST URL (If You Haven't Already)

1. In the Logic app designer, click the first tile: **When a HTTP request is received**.
2. Expand it if needed (click the down chevron).
3. Find **HTTP POST URL**.
4. Click **Copy** next to the URL.
5. The URL looks like: `https://prod-xx.westus.logic.azure.com:443/workflows/...?api-version=2016-06-01&sp=...&sv=...&sig=...`
6. Store this URL securely – you will paste it into the ADF pipeline.

---

## Part 5: Enable the Logic App

1. In the left menu of your Logic App, click **Overview**.
2. Check **Status** at the top. It should show **Enabled**.
3. If it shows **Disabled**, click **Enable** (or go to **Workflow settings** and turn it on).

---

## Part 6: Configure ADF Pipeline to Use This Logic App

1. Open [Azure Data Factory](https://portal.azure.com) → your Data Factory.
2. Click **Open Azure Data Factory Studio** (or **Author & Monitor**).
3. In the left pane, expand **Pipelines** and open **Pl_SqlToSnowflake**.
4. In the pipeline canvas, click on empty space (not on an activity) so the **Pipeline** properties appear in the right panel.
5. Go to the **Parameters** tab (or **General** → **Parameters**).
6. Find **LogicAppAlertUrl**.
7. Set **Default value** to the HTTP POST URL you copied (the full URL including `https://` and the query string).
8. Click **Publish all** (top bar) to save your changes.

When any pipeline activity (Lookup, Copy, or Stored Proc) fails, ADF will POST the failure details to this URL and the Logic App will send you an email.

**To disable alerts:** Set **LogicAppAlertUrl** to empty (`""`) or remove the default value. The Web activities will not send alerts when the URL is empty.

---

## Part 7: Test the Logic App (Optional)

1. In the Logic App designer, click **Run trigger** (dropdown) → **Run**.
2. You'll see **Test the Logic App with sample data**.
3. Either leave the default sample body or paste:

```json
{
    "pipelineName": "Pl_SqlToSnowflake",
    "runId": "test-run-123",
    "status": "Failed",
    "failedActivity": "Copy_Leads_SqlToSnowflake",
    "errorMessage": "Test error message"
}
```

4. Click **Run**.
5. Check your email – you should receive the alert within a minute.

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| **"Use sample payload to generate schema" not visible** | Expand the HTTP trigger tile (click the header). It may be under **Schema** or **Advanced options**. |
| **Send email action shows "Invalid" or connection error** | Re-authorize the connector: click the connector in the action, then **Change connection** → **Add new connection** and sign in again. |
| **No email received** | Check your Spam/Junk folder. For Office 365, ensure the sender is allowed. Run a test (Part 7) to verify. |
| **ADF Web activity fails with 401/403** | The Logic App URL may have expired. Re-copy the HTTP POST URL from the Logic App and update the ADF parameter. |
| **Dynamic content not showing trigger fields** | Save the Logic App first, then add the Send email action. The trigger output should appear in **Add dynamic content**. |
| **Logic App shows "Disabled"** | Go to **Overview** → ensure **Enabled** is selected. |

---

## Request Body Schema (Reference)

The ADF pipeline sends this JSON when a failure occurs:

| Field | Type | Description |
|-------|------|-------------|
| pipelineName | string | Name of the failed pipeline (e.g. Pl_SqlToSnowflake) |
| runId | string | ADF pipeline run ID (for correlating in Azure Portal) |
| status | string | Usually "Failed" |
| failedActivity | string | Name of the activity that failed |
| errorMessage | string | Error details from the failed activity |
