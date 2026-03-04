-- Step 3.1: Create warehouse
-- Run in Snowflake worksheet (ACCOUNTADMIN or similar)

CREATE WAREHOUSE IF NOT EXISTS LEAD_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;
