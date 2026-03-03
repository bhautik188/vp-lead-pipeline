-- Stored procedure to update watermark after ADF incremental copy
USE LeadManagement;
GO

CREATE OR ALTER PROCEDURE sp_UpdateLeadsWatermark
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE DataFactoryWatermark
    SET LastWatermark = (SELECT ISNULL(MAX(UpdatedDateUtc), LastWatermark) FROM Leads)
    WHERE TableName = 'Leads';
END;
GO
