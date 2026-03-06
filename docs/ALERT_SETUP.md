# ADF Pipeline Failure Alert Setup

Step-by-step guide to create an alert that notifies you when **PlLeadsSqlToSnowflake** fails. Works on Azure trial.

---

## Method: Azure Monitor (recommended)

Use the **global Monitor** service — it has the full set of options (Email, Logic App, etc.).

---

## Step 1: Open Monitor and create alert rule

1. Go to [portal.azure.com](https://portal.azure.com)
2. In the top search bar, type **Monitor** and select **Monitor**
3. In the left menu, click **Alerts**
4. Click **+ Create** → **Alert rule**

---

## Step 2: Select scope (your Data Factory)

1. Under **Scope**, click **Select scope**
2. **Subscription:** Your subscription
3. **Resource type:** Select **Data factories**
4. **Resource:** Select **lead-adf** (your Data Factory)
5. Click **Done**

---

## Step 3: Add condition (when to fire)

1. Under **Condition**, click **Add condition**
2. Search for **Failed pipeline runs** (or browse **Data Factory** metrics)
3. Select **Failed pipeline runs metrics**
4. Click **Done**

---

## Step 4: Configure alert logic

1. **Dimension: Name** → Select **PlLeadsSqlToSnowflake**
2. **Dimension: FailureType** → Select all (UserError, SystemError, BadGateway)
3. **Condition:** Greater than
4. **Threshold:** 0
5. **Period:** 5 minutes (or 15 for lower cost on trial)
6. **Frequency:** 5 minutes (or 15 for lower cost)
7. Click **Done**

---

## Step 5: Create action group (notifications)

1. Under **Actions**, click **Create action group** (or **Select action group** if you have one)
2. **Basics** tab:
   - **Subscription:** Your subscription
   - **Resource group:** `rg-adf-alerts` (or `lead-adf-rg`)
   - **Action group name:** `ag-adf-failure`
   - **Display name:** `adffail`
3. Click **Next: Notifications >**

---

## Step 6: Add email notification

1. **Notifications** tab
2. **Notification type:** Email/SMS/Push/Voice
3. **Name:** `email-alert`
4. Check **Email**
5. Enter your email (e.g. `bhautikposhiya123@gmail.com`)
6. Click **OK**
7. Click **Next: Actions >**

---

## Step 7: Add Logic App (optional)

1. **Actions** tab
2. **Action type:** Logic App
3. **Name:** `logic-app-alert`
4. **Subscription:** Your subscription
5. **Resource group:** `rg-adf-alerts` (where LogicApp-ADF-FailureAlert lives)
6. **Logic App:** Select **LogicApp-ADF-FailureAlert**
7. **Identity** (if asked): Leave default or select **System assigned** — the alert will call the Logic App via its HTTP trigger
8. Click **OK**
9. Click **Review + create**
10. Click **Create**

---

## Step 8: Finish alert rule

1. Back on the alert rule screen, under **Actions** you should see your action group
2. **Alert rule name:** `Alert-ADF-Pipeline-Failure`
3. **Description:** (optional) e.g. `Fires when PlLeadsSqlToSnowflake fails`
4. **Severity:** Sev 2
5. **Enable rule upon creation:** **On**
6. Click **Create alert rule**

---

## Quick reference: where to find things

| What | Where |
|------|-------|
| Monitor | Search "Monitor" in Azure Portal top bar |
| Alerts | Monitor → Alerts |
| Create alert | Alerts → + Create → Alert rule |
| Scope | Select lead-adf (Data Factory) |
| Condition | Failed pipeline runs metrics |
| Action group | Create new → Notifications (Email) + Actions (Logic App) |

---

## Trial-friendly settings

| Setting | Value | Saves cost |
|---------|-------|------------|
| Period | 15 minutes | Yes |
| Frequency | 15 minutes | Yes |
| Logic App | Skip if not needed | Yes |
| Email only | Use for notifications | Free |

---

## Verify

1. **Monitor** → **Alerts** → **Alert rules** → Your rule should show **Enabled**
2. Trigger a pipeline failure (e.g. break something temporarily)
3. Within 5–15 minutes you should get an email (and Logic App run if configured)
