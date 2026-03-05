"""
Prepare ADF linked service config from .env.
Reads SQL credentials from .env and optionally Snowflake from SNOWFLAKE_* vars.
Outputs to adf-config/ (gitignored) for import into Azure Data Factory.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    out_dir = PROJECT_ROOT / "adf-config" / "linkedService"
    out_dir.mkdir(parents=True, exist_ok=True)

    # SQL Server or Azure SQL (from .env)
    sql_server = os.getenv("SQL_SERVER", "localhost")
    sql_port = os.getenv("SQL_SERVER_PORT", "1433")
    sql_db = os.getenv("SQL_DATABASE", "LeadManagement")
    sql_user = os.getenv("SQL_USER", "sa")
    sql_pwd = os.getenv("SQL_PASSWORD")
    if not sql_pwd:
        print("Warning: SQL_PASSWORD not set in .env")
        sql_pwd = "<your-password>"

    is_azure_sql = "database.windows.net" in sql_server

    if is_azure_sql:
        # Azure SQL Database: use AzureSqlDatabase, AutoResolve (no Self-hosted IR)
        conn_str = (
            f"Server=tcp:{sql_server},{sql_port};Initial Catalog={sql_db};"
            f"User ID={sql_user};Password={sql_pwd};Encrypt=True;TrustServerCertificate=False;"
        )
        ls_sql = {
            "name": "LsSqlServer",
            "properties": {
                "type": "AzureSqlDatabase",
                "typeProperties": {
                    "connectionString": conn_str,
                },
                "connectVia": {
                    "referenceName": "AutoResolveIntegrationRuntime",
                    "type": "IntegrationRuntimeReference",
                },
            },
        }
        print("Detected Azure SQL Database – using AutoResolveIntegrationRuntime")
    else:
        # On-prem SQL Server: use Self-hosted IR if set
        sql_ir = os.getenv("SELF_HOSTED_IR_NAME", "AutoResolveIntegrationRuntime")
        ls_sql = {
            "name": "LsSqlServer",
            "properties": {
                "type": "SqlServer",
                "typeProperties": {
                    "server": f"{sql_server},{sql_port}",
                    "database": sql_db,
                    "authenticationType": "SQL",
                    "userName": sql_user,
                    "password": {"type": "SecureString", "value": sql_pwd},
                },
                "connectVia": {
                    "referenceName": sql_ir,
                    "type": "IntegrationRuntimeReference",
                },
            },
        }

    (out_dir / "LsSqlServer.json").write_text(json.dumps(ls_sql, indent=2))
    print(f"Wrote {out_dir / 'LsSqlServer.json'}")

    # Snowflake (from SNOWFLAKE_* env vars)
    sf_account = os.getenv("SNOWFLAKE_ACCOUNT", "<org-account>")
    sf_database = os.getenv("SNOWFLAKE_DATABASE", "LEADMANAGEMENT")
    sf_warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "LEAD_WH")
    sf_user = os.getenv("SNOWFLAKE_USER", "<snowflake-username>")
    sf_pwd = os.getenv("SNOWFLAKE_PASSWORD", "<snowflake-password>")

    ls_sf = {
        "name": "LsSnowflake",
        "properties": {
            "type": "SnowflakeV2",
            "typeProperties": {
                "accountIdentifier": sf_account,
                "database": sf_database,
                "warehouse": sf_warehouse,
                "authenticationType": "Basic",
                "user": sf_user,
                "password": {"type": "SecureString", "value": sf_pwd},
            },
            "connectVia": {
                "referenceName": "AutoResolveIntegrationRuntime",
                "type": "IntegrationRuntimeReference",
            },
        },
    }
    (out_dir / "LsSnowflake.json").write_text(json.dumps(ls_sf, indent=2))
    print(f"Wrote {out_dir / 'LsSnowflake.json'}")

    print("\nFor local SQL Server, add to .env:")
    print("  SELF_HOSTED_IR_NAME=SelfHostedIR  # Name of your Self-hosted IR in ADF")
    print("\nAdd to .env for Snowflake:")
    print("  SNOWFLAKE_ACCOUNT=your-org-account")
    print("  SNOWFLAKE_DATABASE=LEADMANAGEMENT")
    print("  SNOWFLAKE_WAREHOUSE=LEAD_WH")
    print("  SNOWFLAKE_USER=your-user")
    print("  SNOWFLAKE_PASSWORD=your-password")


if __name__ == "__main__":
    main()
