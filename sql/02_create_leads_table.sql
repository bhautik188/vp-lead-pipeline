-- Step 2: Create the Leads table
-- Run after 01_create_database.sql
-- RowId allows multiple rows per Id (same lead, different state/email).

USE LeadManagement;
GO

CREATE TABLE Leads (
    RowId INT IDENTITY(1,1) PRIMARY KEY,
    Id UNIQUEIDENTIFIER NOT NULL,
    State INT NOT NULL,
    CreatedDateUtc DATETIME2,
    CancellationRequestDateUtc DATETIME2,
    CancellationDateUtc DATETIME2,
    CancellationRejectionDateUtc DATETIME2,
    SoldEmployee NVARCHAR(255),
    CancelledEmployee NVARCHAR(255),
    UpdatedDateUtc DATETIME2
);
GO
