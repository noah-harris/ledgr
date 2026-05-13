import os
from sqlalchemy import create_engine
from contextlib import contextmanager

USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
EXTERNAL_PORT = os.getenv("EXTERNAL_PORT")

@contextmanager
def get_connection(database:str):
    cxnstr = f"mssql+pyodbc://{USERNAME}:{PASSWORD}@127.0.0.1,{EXTERNAL_PORT}/{database}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
    engine = create_engine(cxnstr, pool_pre_ping=True, connect_args={"timeout": 2})
    conn = engine.connect()
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.commit()
        conn.close()
        engine.dispose()
