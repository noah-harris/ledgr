from db import get_autocommit_connection
import os
from sqlalchemy import text

BUDGET_TOOL_USERNAME = os.getenv("BUDGET_TOOL_USERNAME")
BUDGET_TOOL_PASSWORD = os.getenv("BUDGET_TOOL_PASSWORD")
BUDGET_TOOL_HOST = os.getenv("BUDGET_TOOL_HOST")
BUDGET_TOOL_PORT = os.getenv("BUDGET_TOOL_PORT")

def run():
    with get_autocommit_connection("ldr") as conn:
        conn.execute(text(f"""
            EXEC sp_addlinkedserver
                @server      = N'BudgetTool',
                @srvproduct  = N'',
                @provider    = N'MSOLEDBSQL19',
                @datasrc     = N'{BUDGET_TOOL_HOST},{BUDGET_TOOL_PORT}',
                @provstr    = N'TrustServerCertificate=yes;'

            EXEC sp_addlinkedsrvlogin
                @rmtsrvname  = N'BudgetTool',
                @useself     = N'False',
                @locallogin  = NULL,
                @rmtuser     = '{BUDGET_TOOL_USERNAME}',
                @rmtpassword = '{BUDGET_TOOL_PASSWORD}';
        """))
run()