"""
Load Leads data from Excel into SQL Server.
Reads Data Enginnering Task Dummy Data.xlsx and inserts all 100 rows (no deduplication).

Usage:
    Set .env with SQL_SERVER_CONNECTION_STRING or individual vars, then:
    python load_leads_to_sql.py
"""

import os
import sys
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def get_connection_params() -> dict:
    """Build SQL Server connection params from environment."""
    server = os.getenv("SQL_SERVER", "localhost")
    port = os.getenv("SQL_SERVER_PORT", "1433")
    database = os.getenv("SQL_DATABASE", "LeadManagement")
    user = os.getenv("SQL_USER", "sa")
    password = os.getenv("SQL_PASSWORD")

    if not password:
        raise ValueError(
            "Set SQL_PASSWORD in .env or provide SQL_SERVER_CONNECTION_STRING"
        )
    return {"server": server, "port": port, "database": database, "user": user, "password": password}


def load_excel_to_dataframe(excel_path: Path) -> pd.DataFrame:
    """Load Leads data from Excel. Column names per task PDF (Excel Data Columns)."""
    df = pd.read_excel(excel_path)
    # Task PDF schema: CancelledEmployee. Align if source uses different spelling.
    if "CancelledEmployee" not in df.columns and "CanceledEmployee" in df.columns:
        df["CancelledEmployee"] = df["CanceledEmployee"]
    cols = [
        "Id", "State", "CreatedDateUtc", "CancellationRequestDateUtc",
        "CancellationDateUtc", "CancellationRejectionDateUtc",
        "SoldEmployee", "CancelledEmployee", "UpdatedDateUtc",
    ]
    return df[[c for c in cols if c in df.columns]]


def insert_leads_to_sql(df: pd.DataFrame, params: dict) -> int:
    """Insert Leads dataframe into SQL Server. Creates database and table if needed."""
    try:
        from sqlalchemy import create_engine, text
        from urllib.parse import quote_plus

        def make_url(db: str) -> str:
            return (
                f"mssql+pymssql://{params['user']}:{quote_plus(params['password'])}@"
                f"{params['server']}:{params['port']}/{db}"
            )

        engine_master = create_engine(make_url("master"))

        last_err = None
        for attempt in range(6):
            try:
                with engine_master.connect() as conn:
                    conn.execute(text("SELECT 1"))
                break
            except Exception as e:
                last_err = e
                if attempt < 5:
                    time.sleep(5)
        else:
            raise last_err

        db = params["database"]
        with engine_master.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text(f"IF DB_ID('{db}') IS NULL CREATE DATABASE [{db}]"))

        engine = create_engine(make_url(db))
        with engine.connect() as conn:
            conn.execute(text("IF OBJECT_ID('dbo.Leads') IS NOT NULL DROP TABLE Leads"))
            conn.execute(text("""
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
                )
            """))
            conn.commit()

        count = len(df)
        df.to_sql(
            name="Leads",
            con=engine,
            schema="dbo",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=50,
        )

        # Step 2: create watermark table and stored proc for ADF incremental loads
        with engine.connect() as conn:
            conn.execute(text("""
                IF OBJECT_ID('dbo.adt_watermark') IS NULL
                CREATE TABLE dbo.adt_watermark (
                    TableName NVARCHAR(128) NOT NULL PRIMARY KEY,
                    WatermarkValue DATETIME2 NOT NULL,
                    LastModified DATETIME2 NOT NULL DEFAULT GETUTCDATE()
                )
            """))
            conn.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM dbo.adt_watermark WHERE TableName = 'Leads')
                INSERT INTO dbo.adt_watermark (TableName, WatermarkValue, LastModified)
                VALUES (N'Leads', '1900-01-01', GETUTCDATE())
            """))
            conn.execute(text("""
                CREATE OR ALTER PROCEDURE dbo.sp_UpdateWatermark
                    @TableName NVARCHAR(128), @OldWatermark DATETIME2
                AS
                BEGIN
                    SET NOCOUNT ON;
                    DECLARE @NewWatermark DATETIME2 = (
                        SELECT ISNULL(MAX(UpdatedDateUtc), @OldWatermark)
                        FROM dbo.Leads WHERE UpdatedDateUtc > @OldWatermark
                    );
                    UPDATE dbo.adt_watermark
                    SET WatermarkValue = @NewWatermark, LastModified = GETUTCDATE()
                    WHERE TableName = @TableName;
                END
            """))
            conn.commit()

        return count
    except ImportError:
        print("Install: pip install pymssql sqlalchemy", file=sys.stderr)
        raise


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    excel_path = script_dir / "Data Enginnering Task Dummy Data.xlsx"

    if not excel_path.exists():
        print(f"Error: Excel file not found at {excel_path}", file=sys.stderr)
        sys.exit(1)

    try:
        df = load_excel_to_dataframe(excel_path)
        print(f"Loaded {len(df)} rows from Excel")

        params = get_connection_params()
        inserted = insert_leads_to_sql(df, params)
        print(f"Inserted {inserted} rows into Leads table (watermark table ready for Step 2 ADF)")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
