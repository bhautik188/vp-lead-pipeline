#!/bin/bash
# Start SQL Server in Docker for Lead Management project
# Password must match .env SQL_PASSWORD (Bhautik1!)

docker rm -f sqlserver 2>/dev/null || true
docker run -e "ACCEPT_EULA=Y" -e 'MSSQL_SA_PASSWORD=Bhautik1!' \
  -p 1433:1433 --name sqlserver \
  -d mcr.microsoft.com/mssql/server:2022-latest

echo "Starting SQL Server... wait ~20 seconds, then run: python load_leads_to_sql.py"
