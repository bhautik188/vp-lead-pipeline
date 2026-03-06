"""
Transform LEADS to LeadEvents in Snowflake (Step 4).

Reads from Snowflake LEADS table, applies event transformation rules per
Data_Engineering_Task.pdf, and writes to LeadEvents table.

Transformation rules:
  State 0 → LeadSold (SoldEmployee, CreatedDateUtc)
  State 1 → LeadCancellationRequested ("Unknown", CancellationRequestDateUtc)
  State 2 → LeadCancelled (CancelledEmployee, CancellationDateUtc)
  State 3 → LeadCancellationRejected ("Unknown", CancellationRejectionDateUtc)

Usage:
    Set .env with SNOWFLAKE_* vars, then (from project root):
    python scripts/transform_leads_to_leadevents.py
"""

import os
import sys
import uuid
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv

# Load .env from project root (works when run from any directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Event type constants per task specification
EVENT_LEAD_SOLD = "LeadSold"
EVENT_LEAD_CANCELLATION_REQUESTED = "LeadCancellationRequested"
EVENT_LEAD_CANCELLED = "LeadCancelled"
EVENT_LEAD_CANCELLATION_REJECTED = "LeadCancellationRejected"
UNKNOWN_EMPLOYEE = "Unknown"


class SnowflakeConnection:
    """
    Snowflake connection manager using OOP and context manager pattern.
    Loads credentials from .env; no hardcoded secrets.
    """

    def __init__(self) -> None:
        self._conn: Any = None

    def _get_config(self) -> dict:
        """Build connection config from environment variables."""
        account = os.getenv("SNOWFLAKE_ACCOUNT")
        user = os.getenv("SNOWFLAKE_USER")
        password = os.getenv("SNOWFLAKE_PASSWORD")
        database = os.getenv("SNOWFLAKE_DATABASE", "LEADMANAGEMENT")
        warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "LEAD_WH")
        schema = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")

        if not all([account, user, password]):
            raise ValueError(
                "Set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and SNOWFLAKE_PASSWORD in .env"
            )

        return {
            "account": account,
            "user": user,
            "password": password,
            "database": database,
            "warehouse": warehouse,
            "schema": schema,
        }

    def connect(self) -> "SnowflakeConnection":
        """Establish connection to Snowflake."""
        try:
            import snowflake.connector
        except ImportError:
            raise ImportError(
                "Install snowflake-connector-python: pip install snowflake-connector-python"
            )

        config = self._get_config()
        self._conn = snowflake.connector.connect(
            account=config["account"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            warehouse=config["warehouse"],
            schema=config["schema"],
        )
        return self

    def close(self) -> None:
        """Close the connection."""
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def __enter__(self) -> "SnowflakeConnection":
        return self.connect()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    @property
    def connection(self) -> Any:
        """Return the underlying connection object."""
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() or use as context manager.")
        return self._conn

    def execute(self, sql: str, params: Optional[tuple] = None) -> Any:
        """Execute a query and return the cursor."""
        cursor = self.connection.cursor()
        cursor.execute(sql, params or ())
        return cursor


def transform_lead_to_event(row: dict) -> Optional[dict]:
    """
    Transform a single LEADS row to a LeadEvents row per task rules.
    Returns None if the row cannot be transformed (e.g. invalid state).
    """
    state = row.get("STATE")
    if state is None:
        return None

    lead_id = row.get("ID")
    updated_utc = row.get("UPDATEDDATEUTC")

    if state == 0:
        return {
            "Id": str(uuid.uuid4()),
            "EventType": EVENT_LEAD_SOLD,
            "EventEmployee": row.get("SOLDEMPLOYEE") or UNKNOWN_EMPLOYEE,
            "EventDate": row.get("CREATEDDATEUTC") or updated_utc,
            "LeadId": lead_id,
            "UpdatedDateUtc": updated_utc,
        }
    if state == 1:
        return {
            "Id": str(uuid.uuid4()),
            "EventType": EVENT_LEAD_CANCELLATION_REQUESTED,
            "EventEmployee": UNKNOWN_EMPLOYEE,
            "EventDate": row.get("CANCELLATIONREQUESTDATEUTC") or updated_utc,
            "LeadId": lead_id,
            "UpdatedDateUtc": updated_utc,
        }
    if state == 2:
        return {
            "Id": str(uuid.uuid4()),
            "EventType": EVENT_LEAD_CANCELLED,
            "EventEmployee": row.get("CANCELLEDEMPLOYEE") or UNKNOWN_EMPLOYEE,
            "EventDate": row.get("CANCELLATIONDATEUTC") or updated_utc,
            "LeadId": lead_id,
            "UpdatedDateUtc": updated_utc,
        }
    if state == 3:
        return {
            "Id": str(uuid.uuid4()),
            "EventType": EVENT_LEAD_CANCELLATION_REJECTED,
            "EventEmployee": UNKNOWN_EMPLOYEE,
            "EventDate": row.get("CANCELLATIONREJECTIONDATEUTC") or updated_utc,
            "LeadId": lead_id,
            "UpdatedDateUtc": updated_utc,
        }

    return None


def run_transform(conn: SnowflakeConnection) -> int:
    """
    Read LEADS from Snowflake, transform to LeadEvents, and insert.
    Returns the number of events inserted.
    """
    cursor = conn.execute(
        "SELECT ID, STATE, CREATEDDATEUTC, CANCELLATIONREQUESTDATEUTC, "
        "CANCELLATIONDATEUTC, CANCELLATIONREJECTIONDATEUTC, "
        "SOLDEMPLOYEE, CANCELLEDEMPLOYEE, UPDATEDDATEUTC FROM LEADS"
    )
    columns = [c[0] for c in cursor.description]
    rows = cursor.fetchall()

    events = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        event = transform_lead_to_event(row_dict)
        if event:
            events.append(event)

    if not events:
        return 0

    # Truncate and insert (idempotent for full refresh)
    conn.execute("TRUNCATE TABLE LEADEVENTS")

    insert_sql = (
        "INSERT INTO LEADEVENTS (ID, EVENTTYPE, EVENTEMPLOYEE, EVENTDATE, LEADID, UPDATEDDATEUTC) "
        "VALUES (%s, %s, %s, %s, %s, %s)"
    )
    cursor = conn.connection.cursor()
    for e in events:
        cursor.execute(
            insert_sql,
            (
                e["Id"],
                e["EventType"],
                e["EventEmployee"],
                e["EventDate"],
                e["LeadId"],
                e["UpdatedDateUtc"],
            ),
        )
    conn.connection.commit()

    return len(events)


def main() -> None:
    """Main entry point: connect, transform, and write LeadEvents."""
    try:
        with SnowflakeConnection() as conn:
            count = run_transform(conn)
            print(f"Transformed {count} leads into LeadEvents")
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except ImportError as e:
        print(f"Dependency error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
