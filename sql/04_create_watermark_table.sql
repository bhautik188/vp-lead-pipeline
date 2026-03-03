-- Watermark table for ADF incremental load
-- Stores last copied watermark per table for incremental loads

USE LeadManagement;
GO

CREATE TABLE DataFactoryWatermark (
    TableName NVARCHAR(128) PRIMARY KEY,
    LastWatermark DATETIME2 NOT NULL DEFAULT '1900-01-01'
);

-- Insert initial row for Leads
INSERT INTO DataFactoryWatermark (TableName, LastWatermark)
VALUES ('Leads', '1900-01-01');
GO
