from db import get_connection
from sqlalchemy import text
from config import *

def create():
    logger.debug("RECREATING DATABASE [ldr]...")
    with get_connection(db="master") as conn:
        conn.execute(text("CREATE DATABASE [ldr]"))

    logger.debug("CREATING DATABASE OBJECTS...")
    with get_connection() as conn:
        for f in BUILD_ORDER:
            logger.debug(f"Creating {f[1]}...")
            with open(f"db-init/{f[0]}/{f[1]}.sql", "r", encoding="utf-8-sig") as sql_file:
                sql = sql_file.read()
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                logger.critical(f"Error creating {f[1]}: {e}", exc=type(e))

create()