-- Step 4: Watermark table for ADF incremental loads
-- Run after 03_insert_leads_data.sql (or use load_leads_to_sql.py – it creates this automatically)

USE LeadManagement;
GO

-- Control table for pipeline watermark (incremental load)
CREATE TABLE dbo.adt_watermark (
    TableName     NVARCHAR(128) NOT NULL PRIMARY KEY,
    WatermarkValue DATETIME2 NOT NULL,
    LastModified   DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);

-- Insert initial watermark for Leads (copy all data on first run)
INSERT INTO dbo.adt_watermark (TableName, WatermarkValue, LastModified)
VALUES (
    N'Leads',
    '1900-01-01 00:00:00.000',
    GETUTCDATE()
);
GO

-- Stored procedure: computes new watermark from Leads and updates table
CREATE OR ALTER PROCEDURE dbo.sp_UpdateWatermark
    @TableName   NVARCHAR(128),
    @OldWatermark DATETIME2
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @NewWatermark DATETIME2 = (
        SELECT ISNULL(MAX(UpdatedDateUtc), @OldWatermark)
        FROM dbo.Leads
        WHERE UpdatedDateUtc > @OldWatermark
    );
    UPDATE dbo.adt_watermark
    SET WatermarkValue = @NewWatermark, LastModified = GETUTCDATE()
    WHERE TableName = @TableName;
END;
GO
